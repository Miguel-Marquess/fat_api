import factory
import pytest
from factory import fuzzy

from fast_zero.models.db_models import TaskDataBase
from fast_zero.schemas.tasks_schemas import TaskState


class TaskFactory(factory.Factory):
    class Meta:
        model = TaskDataBase

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = fuzzy.FuzzyChoice(TaskState)
    # fuzzy escolhe elementos aleatorios de algo
    # passado


@pytest.mark.asyncio
async def test_task_should_return_many_tasks(session, client, user, token):
    len_tasks = 10
    session.add_all(TaskFactory.create_batch(len_tasks, user_id=user.id))
    # na async def, add_all() adiciona varios elementos na session
    # de uma vez
    await session.commit()

    response = client.get(
        '/tasks', headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['tasks']) == len_tasks


@pytest.mark.asyncio
async def test_task_limit_offset_should_return_2_todos(
    client, token, session, user
):
    expected_tasks = 2
    session.add_all(TaskFactory.create_batch(5, user_id=user.id))

    await session.commit()

    response = client.get(
        '/tasks/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['tasks']) == expected_tasks


@pytest.mark.asyncio
async def test_task_title_should_return_5_todos(client, token, session, user):
    expected_tasks = 5
    session.add_all(
        TaskFactory.create_batch(
            expected_tasks, user_id=user.id, title='test_tasks'
        )
    )
    session.add_all(
        TaskFactory.create_batch(
            expected_tasks,
            user_id=user.id,
        )
    )

    await session.commit()

    response = client.get(
        '/tasks/?title=test_tasks',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['tasks']) == expected_tasks


@pytest.mark.asyncio
async def test_task_description_should_return_5_todos(
    client, token, session, user
):
    expected_tasks = 5
    session.add_all(
        TaskFactory.create_batch(
            expected_tasks,
            user_id=user.id,
            description='test_tasks.description',
        )
    )

    session.add_all(
        TaskFactory.create_batch(
            expected_tasks,
            user_id=user.id,
        )
    )

    await session.commit()

    response = client.get(
        '/tasks/?description=test_tasks.descr',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['tasks']) == expected_tasks


@pytest.mark.asyncio
async def test_task_state_should_return_5_todos(client, token, session, user):
    expected_tasks = 5
    session.add_all(
        TaskFactory.create_batch(
            expected_tasks,
            user_id=user.id,
            state=TaskState.done,
        )
    )

    session.add_all(
        TaskFactory.create_batch(
            expected_tasks, user_id=user.id, state=TaskState.doing
        )
    )

    await session.commit()

    response = client.get(
        '/tasks/?state=done',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['tasks']) == expected_tasks
