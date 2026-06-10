from http import HTTPStatus

import pytest

from tests.test_tasks.test_todos import TaskFactory


def test_update_not_found(client, token):
    response = client.patch(
        '/tasks/10', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.json() == {'detail': 'Task not found.'}
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_update_other_task_user(client, token, other_user, session):
    task = TaskFactory(user_id=other_user.id)
    session.add(task)
    await session.commit()
    response = client.patch(
        '/tasks/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.json() == {'detail': 'Task not found.'}
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_update_task(client, user, token, session):
    task = TaskFactory(user_id=user.id)
    session.add(task)
    await session.commit()
    response = client.patch(
        '/tasks/1',
        headers={'Authorization': f'Bearer {token}'},
        params={'title': 'test1'},
        # params passa via query parameters
    )

    assert response.json()['title'] == 'test1'
