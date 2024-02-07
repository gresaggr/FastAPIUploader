import logging

from fastapi import HTTPException, APIRouter
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

from dao.db import create_user_db

from src.auth.auth import login_for_access_token
from src.settings import templates

router = APIRouter(prefix='/auth', tags=['users'])


@router.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    context = {
        "request": request,
    }
    return templates.TemplateResponse("register.html", context)


class RegisterForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: list = []
        self.username: str | None = None
        self.password: str | None = None
        self.password2: str | None = None

    async def load_data(self):
        form = await self.request.form()
        self.username = form.get("username")
        self.password = form.get("password")
        self.password2 = form.get("password2")

    async def is_valid(self):
        # if not self.username or not (self.username.__contains__("@")):
        if not self.username:
            self.errors.append("Требуется ввод username")
        if not self.password:
            self.errors.append("Требуется ввода пароля")
        if not self.password2:
            self.errors.append("Требуется ввода подтверждения пароля")
        if self.password != self.password2:
            self.errors.append("Пароли не совпадают!")
        if not self.errors:
            return True
        return False


@router.post("/register", response_class=HTMLResponse)
async def register_post(request: Request):
    form = RegisterForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            response = RedirectResponse("/", status.HTTP_302_FOUND)
            user = await create_user_db(form.username, form.password)
            if not user:
                form.__dict__.update(msg="")
                form.__dict__.get("errors").append("Ошибка регистрации пользователя")
                return templates.TemplateResponse("register.html", form.__dict__)
            else:
                await login_for_access_token(response=response, form_data=form)
                form.__dict__.update(msg="Успешная регистрация!")
                logging.info("Успешная регистрация!")
                return response
        except HTTPException:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append("Incorrect Email or Password")
            return templates.TemplateResponse("register.html", form.__dict__)
    return templates.TemplateResponse("register.html", form.__dict__)
