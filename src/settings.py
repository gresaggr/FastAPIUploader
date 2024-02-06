from environs import Env

env = Env()
env.read_env()  # не обязательно указывать путь, найдет даже в родительской


class Settings:
    SECRET_KEY = env.str('SECRET_KEY')
    ALGORITHM = env.str('ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES = 30  # время жизни токена
    COOKIE_NAME = "access_token"


settings = Settings()
