import logging
import os

from fastapi import FastAPI, UploadFile, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from dao.models import User
from src.auth.auth import router as auth_router, get_current_user_from_cookie, get_current_user_from_token, \
    login_for_access_token
from src.logger import set_logger
from src.settings import settings

UPLOAD_DIR = Path(__file__).parent / 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

set_logger()
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.include_router(auth_router)


@app.post('/uploadfile')
async def create_upload_file(wm_file: UploadFile):
    # data = await wm_file.read()
    # wm_fn = UPLOAD_DIR / wm_file.filename
    return {"filename": wm_file.filename}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    try:
        user = await get_current_user_from_cookie(request)
    except:
        user = None
    context = {
        "user": user,
        "request": request,
    }
    return templates.TemplateResponse("index.html", context)


# --------------------------------------------------------------------------
# Private Page
# --------------------------------------------------------------------------
# A private page that only logged-in users can access.
@app.get("/private", response_class=HTMLResponse)
async def index(request: Request, user: User = Depends(get_current_user_from_token)):
    context = {
        "user": user,
        "request": request
    }
    return templates.TemplateResponse("private.html", context)


# --------------------------------------------------------------------------
# Login - GET
# --------------------------------------------------------------------------
@app.get("/auth/login", response_class=HTMLResponse)
async def login_get(request: Request):
    context = {
        "request": request,
    }
    return templates.TemplateResponse("login.html", context)


# --------------------------------------------------------------------------
# Login - POST
# --------------------------------------------------------------------------
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
            self.errors.append("Требуется ввода username")
        if not self.password:
            self.errors.append("Требуется ввода пароля")
        if not self.errors:
            return True
        return False


@app.post("/auth/login", response_class=HTMLResponse)
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


# --------------------------------------------------------------------------
# Logout
# --------------------------------------------------------------------------
@app.get("/auth/logout", response_class=HTMLResponse)
async def login_get():
    response = RedirectResponse(url="/")
    response.delete_cookie(settings.COOKIE_NAME)
    return response
