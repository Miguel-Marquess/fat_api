from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from fast_zero.dependencies import Current_user, T_Session, TaskFilter
from fast_zero.models.db_models import TaskDataBase
from fast_zero.schemas.tasks_schemas import (
    TaskList,
    TaskPublic,
    TaskSchema,
    TaskUpdate,
)
from fast_zero.schemas.users_schemas import Message

router = APIRouter(tags=['tasks'], prefix='/tasks')


@router.post('/', response_model=TaskPublic, status_code=201)
async def create_task(
    todo: TaskSchema, user: Current_user, session: T_Session
):
    db_task = TaskDataBase(**todo.model_dump(), user_id=user.id)

    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)

    return db_task


@router.get('/', response_model=TaskList, status_code=200)
async def get_tasks(user: Current_user, session: T_Session, tasks: TaskFilter):
    query = select(TaskDataBase).where(
        TaskDataBase.user_id == user.id
    )  # query e somente um obj sqla

    # seleciona tudo e filtra depois
    if tasks.title:
        query = query.filter(TaskDataBase.title.contains(tasks.title))
        # constains == like('%l%')
    if tasks.description:
        query = query.filter(
            TaskDataBase.description.contains(tasks.description)
        )
        # filter == where
    if tasks.state:
        query = query.filter(TaskDataBase.state == tasks.state)

    tasks = await session.scalars(
        query.offset(tasks.offset).limit(tasks.limit)
    )

    return {'tasks': tasks.fetchall()}


@router.delete('/{task_id}', response_model=Message)
async def delete_tasks(task_id: int, session: T_Session, user: Current_user):
    task = await session.scalar(
        select(TaskDataBase).where(
            TaskDataBase.id == task_id, TaskDataBase.user_id == user.id
        )
    )

    if task:
        await session.delete(task)
        await session.commit()
        return {'message': 'Task was deleted.'}
    raise HTTPException(status_code=404, detail='Task not exist.')


@router.patch('/{task_id}', response_model=TaskPublic)
async def update_task(
    task_id: int,
    task: Annotated[TaskUpdate, Query()],
    user: Current_user,
    session: T_Session,
):
    db_task = await session.scalar(
        select(TaskDataBase).where(
            TaskDataBase.id == task_id, TaskDataBase.user_id == user.id
        )
    )

    if not db_task:
        raise HTTPException(status_code=404, detail='Task not found.')

    for key, value in task.model_dump(exclude_unset=True).items():
        setattr(db_task, key, value)
        # obj.atributo = valor
        # atualiza diretamente o ORM

    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)
    return db_task
