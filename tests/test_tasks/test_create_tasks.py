from dataclasses import asdict
from http import HTTPStatus

from fast_zero.schemas.tasks_schemas import TaskPublic
from tests.test_tasks.test_todos import TaskFactory


def test_create_task(client, user, token):
    task = TaskFactory(user_id=user.id)
    response = client.post(
        '/tasks',
        headers={'Authorization': f'Bearer {token}'},
        json=asdict(task),
    )
    task.id = 1
    assert (
        response.json()
        == TaskPublic.model_validate(task, from_attributes=True).model_dump()
    )
    assert response.status_code == HTTPStatus.CREATED
