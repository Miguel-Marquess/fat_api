from datetime import datetime

from sqlalchemy import ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

from fast_zero.models.tasks_models import TaskState

registry_table = registry()  # registra as tabelas. PYTHON <--> DB


@registry_table.mapped_as_dataclass
class UserDataBase:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, init=False, primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    # unique nao permite dados iguais
    password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, onupdate=func.now(), server_default=func.now()
    )

    # relacionamento de user <> task
    user_tasks: Mapped[list['TaskDataBase']] = relationship(
        init=False,
        cascade='all, delete-orphan',  # apagou user, apaga as tasks
        # delete-orphan = delete as tasks orfaos (sem user)
        lazy='selectin',  # seleciona todas as tasks dos users
        # de uma vez
    )


@registry_table.mapped_as_dataclass
class TaskDataBase:
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    state: Mapped[TaskState]  # So podera ser armazenado na tabela
    # elementos do tipo TaskState

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
