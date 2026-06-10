from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from fast_zero.models.db_models import UserDataBase, registry_table
from fast_zero.settings import Settings

settings = Settings()

engine = create_async_engine(settings.DATABASE_URL)
registry_table.metadata.create_all


async def get_session():  # pragma: no cover
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


async def get_user_by_id(user_id: int, session):
    user_db = await session.scalar(
        select(UserDataBase).where(UserDataBase.id == user_id)
    )
    if user_db:
        return user_db
    return None
