from http import HTTPStatus

import pytest

from tests.test_tasks.test_todos import TaskFactory


@pytest.mark.asyncio
async def test_delete_task(client, user, token, session):
    task = TaskFactory(user_id=user.id)
    session.add(task)
    await session.commit()

    response = client.delete(
        f'/tasks/{task.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.json() == {'message': 'Task was deleted.'}


@pytest.mark.asyncio
async def test_delete_different_user_task(client, other_user, token, session):
    task = TaskFactory(user_id=other_user.id)
    session.add(task)
    await session.commit()

    response = client.delete(
        f'/tasks/{task.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.json() == {'detail': 'Task not exist.'}
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_delete_not_found(client, token):
    response = client.delete(
        '/tasks/0', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.json() == {'detail': 'Task not exist.'}
    assert response.status_code == HTTPStatus.NOT_FOUND
