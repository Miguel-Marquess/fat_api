from dataclasses import asdict
from http import HTTPStatus

import pytest
from pydantic import ValidationError

from fast_zero.models.db_models import TaskDataBase
from fast_zero.schemas.tasks_schemas import TaskPublic, TaskSchema
from tests.test_tasks.test_todos import TaskFactory


def test_create_task(client, user, token, mock_db_time):
    with mock_db_time(model=TaskDataBase) as time:
        task = TaskFactory(user_id=user.id)
        response = client.post(
            '/tasks',
            headers={'Authorization': f'Bearer {token}'},
            json=asdict(task),
        )
        task.id = 1
        task.created_at = time
        task.updated_at = time

        assert (
            response.json()
            == TaskPublic.model_validate(
                task, from_attributes=True
            ).model_dump(mode='json')
            # modo json serializa para formato retornado pela API
            # transformando objetos em strings
        )
        assert response.status_code == HTTPStatus.CREATED


def test_create_task_invalid_state(user):
    with pytest.raises(ValidationError):
        TaskSchema(
            title='test', description='test', state='wrong', user_id=user.id
        )


def test_create_task_unprocessable_state(client, user, token):
    task = TaskFactory(user_id=user.id, state='wrong')
    response = client.post(
        '/tasks',
        headers={'Authorization': f'Bearer {token}'},
        json=asdict(task),
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
