from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from fast_zero.models import UserDataBase, registry_table
from fast_zero.settings import Settings

settings = Settings()

engine = create_engine(settings.DATABASE_URL)
registry_table.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def get_user_by_id(user_id: int, session):
    user_db = session.scalar(
        select(UserDataBase).where(UserDataBase.id == user_id)
    )
    if user_db:
        return user_db
    return None
