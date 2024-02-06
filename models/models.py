from pydantic import BaseModel
from passlib.handlers.sha2_crypt import sha512_crypt as crypto


class User(BaseModel):
    username: str
    hashed_password: str


# тестовая работа: без подключения реальной базы данных. есть только 2 пользователя и пароли у них "12345"
class DataBase(BaseModel):
    user: list[User]


DB = DataBase(
    user=[
        User(username="user1", hashed_password=crypto.hash("12345")),
        User(username="user2", hashed_password=crypto.hash("12345")),
    ]
)


def get_user(username: str) -> User | None:
    user = [user for user in DB.user if user.username == username]
    if user:
        return user[0]
    return None
