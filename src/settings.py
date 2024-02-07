from environs import Env
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import BaseModel

env = Env()
env.read_env()  # не обязательно указывать путь (найдет даже в родительской)

BASE_DIR = Path(__file__).parent.parent

DB_PATH = BASE_DIR / "users.sqlite"


class DbSettings(BaseModel):
    url: str = f"sqlite+aiosqlite:///{DB_PATH}"
    # echo: bool = False
    echo: bool = False


class Settings:
    SECRET_KEY = env.str('SECRET_KEY')
    ALGORITHM = env.str('ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES = 30  # время жизни токена
    COOKIE_NAME = "access_token"

    db: DbSettings = DbSettings()


settings = Settings()
