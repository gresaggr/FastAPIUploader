import datetime as dt
import logging

from fastapi import Depends, HTTPException, Request, Response, status, APIRouter
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2, OAuth2PasswordRequestForm
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
from passlib.handlers.sha2_crypt import sha512_crypt as crypto

from models.models import User, get_user
from src.settings import settings

log = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


# --------------------------------------------------------------------------
# Authentication logic
# --------------------------------------------------------------------------
class OAuth2PasswordBearerWithCookie(OAuth2):
    """
    This class is taken directly from FastAPI:
    https://github.com/tiangolo/fastapi/blob/26f725d259c5dbe3654f221e608b14412c6b40da/fastapi/security/oauth2.py#L140-L171

    The only change made is that authentication is taken from a cookie
    instead of from the header!
    """

    def __init__(
            self,
            token_url: str,
            scheme_name: str | None = None,
            scopes: dict[str, str] | None = None,
            description: str | None = None,
            auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": token_url, "scopes": scopes})
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> str | None:
        # IMPORTANT: this is the line that differs from FastAPI. Here we use
        # `request.cookies.get(settings.COOKIE_NAME)` instead of
        # `request.headers.get("Authorization")`
        authorization: str = request.cookies.get(settings.COOKIE_NAME)
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


oauth2_scheme = OAuth2PasswordBearerWithCookie(token_url="token")


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = dt.datetime.utcnow() + dt.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def authenticate_user(username: str, plain_password: str) -> User | bool:
    user = get_user(username)  # здесь берется из жестко заданных пользователей. TODO: добавить подключение к базе
    if not user:
        return False
    if not crypto.verify(plain_password, user.hashed_password):
        return False
    return user


def decode_token(token: str) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials."
    )
    token = token.removeprefix("Bearer").strip()
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
    except JWTError as e:
        print(e)
        raise credentials_exception

    user = get_user(username)
    return user


def get_current_user_from_token(token: str = Depends(oauth2_scheme)) -> User:
    """
    Get the current user from the cookies in a request.

    Use this function when you want to lock down a route so that only
    authenticated users can see access the route.
    """
    user = decode_token(token)
    return user


def get_current_user_from_cookie(request: Request) -> User:
    """
    Get the current user from the cookies in a request.

    Use this function from inside other routes to get the current user. Good
    for views that should work for both logged in, and not logged-in users.
    """
    token = request.cookies.get(settings.COOKIE_NAME)
    user = decode_token(token)
    return user


@router.post("token")
def login_for_access_token(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends()
) -> dict[str, str]:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token(data={"username": user.username})  # посмотреть можно здесь https://jwt.io/

    # Set an HttpOnly cookie in the response. `httponly=True` prevents
    # JavaScript from reading the cookie.
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=f"Bearer {access_token}",
        httponly=True
    )
    return {settings.COOKIE_NAME: access_token, "token_type": "bearer"}
