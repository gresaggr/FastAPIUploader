from typing import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from passlib.handlers.sha2_crypt import sha512_crypt as crypto

from dao.models import engine, User

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


# async def get_user_db(username: str, session: AsyncSession = Depends(get_async_session)):
async def get_user_db(username: str):
    sql = select(User).where(User.username == username)
    async with async_session_maker() as session:
        query = await session.execute(sql)
        user = query.scalar_one_or_none()
        return user


async def create_user_db(username: str, password: str):
    hashed_password = crypto.hash(password)
    new_user = User(username=username, hashed_password=hashed_password)
    async with async_session_maker() as session:
        session.add(new_user)
        await session.commit()

    return new_user
