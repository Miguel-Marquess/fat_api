from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.models.db_models import TaskDataBase, UserDataBase
from tests.conftest import UserFactory
from tests.test_tasks.test_todos import TaskFactory


@pytest.mark.asyncio
async def test_create_user_db(session: AsyncSession, mock_db_time):
    with mock_db_time(model=UserDataBase) as time:
        user = UserFactory()

        session.add(user)
        await session.commit()

        user_db = await session.scalar(
            select(UserDataBase).where(UserDataBase.username == user.username)
        )

    assert asdict(user_db) == {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'password': user.password,
        'created_at': time,  # aqui recebe o time praq
        # possa fazer a verificacao, o obj time
        'updated_at': time,
        'user_tasks': [],
    }
    # o id e 1 pois sempre o banco esta sendo apagadop(registry.drop_all())


@pytest.mark.asyncio
async def test_create_task_db(session, mock_db_time, user):
    with mock_db_time(model=TaskDataBase):
        task = TaskFactory(user_id=user.id)
        session.add(task)
        await session.commit()

        task_db = await session.scalar(
            select(TaskDataBase).where(
                TaskDataBase.user_id == user.id, TaskDataBase.id == task.id
            )
        )

    assert asdict(task_db) == asdict(task)
