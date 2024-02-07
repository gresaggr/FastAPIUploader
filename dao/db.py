from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker, joinedload

from dao.models import engine, User

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


# async def get_user_db(username: str, session: AsyncSession = Depends(get_async_session)):
async def get_user_db(username: str, session: AsyncSession = Depends(get_async_session)):
    sql = select(User).where(User.username == username)
    async with async_session_maker() as session:
        query = await session.execute(sql)
        user = query.scalar_one_or_none()
        return user
