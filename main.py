import os

from fastapi import FastAPI, UploadFile, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from dao.models import User
from src.api.login import router as login_router
from src.auth.auth import get_current_user_from_cookie, get_current_user_from_token
from src.logger import set_logger
from src.settings import templates

UPLOAD_DIR = Path(__file__).parent / 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

set_logger()
app = FastAPI()
app.include_router(login_router)


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
