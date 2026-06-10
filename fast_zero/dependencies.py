from typing import Annotated

from fastapi import Depends, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.database import get_session
from fast_zero.models.db_models import UserDataBase
from fast_zero.schemas.tasks_schemas import FilterPage, TaskPage
from fast_zero.security import get_current_user

T_Session = Annotated[AsyncSession, Depends(get_session)]
Current_user = Annotated[UserDataBase, Depends(get_current_user)]
T_FilterPage = Annotated[FilterPage, Query()]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
TaskFilter = Annotated[TaskPage, Query()]
