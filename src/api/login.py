import logging

from fastapi import HTTPException, APIRouter
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

from src.auth.auth import login_for_access_token
from src.settings import settings, templates

router = APIRouter(prefix='/auth', tags=['users'])


@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    context = {
        "request": request,
    }
    return templates.TemplateResponse("login.html", context)


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: list = []
        self.username: str | None = None
        self.password: str | None = None

    async def load_data(self):
        form = await self.request.form()
        self.username = form.get("username")
        self.password = form.get("password")

    async def is_valid(self):
        # if not self.username or not (self.username.__contains__("@")):
        if not self.username:
            self.errors.append("Требуется ввод username")
        if not self.password:
            self.errors.append("Требуется ввод пароля")
        if not self.errors:
            return True
        return False


@router.post("/login", response_class=HTMLResponse)
async def login_post(request: Request):
    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            response = RedirectResponse("/", status.HTTP_302_FOUND)
            await login_for_access_token(response=response, form_data=form)
            form.__dict__.update(msg="Успешная авторизация!")
            logging.info("Успешная авторизация")
            return response
        except HTTPException:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append("Incorrect Email or Password")
            return templates.TemplateResponse("login.html", form.__dict__)
    return templates.TemplateResponse("login.html", form.__dict__)


@router.get("/logout", response_class=HTMLResponse)
async def logout_get():
    response = RedirectResponse(url="/")
    response.delete_cookie(settings.COOKIE_NAME)
    return response
