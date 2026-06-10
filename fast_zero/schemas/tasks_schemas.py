from pydantic import BaseModel, ConfigDict, Field

from fast_zero.models.tasks_models import TaskState


class TaskSchema(BaseModel):
    title: str
    description: str
    state: TaskState = Field(default=TaskState.doing)


class TaskPublic(TaskSchema):
    id: int
    model_config = ConfigDict(from_attributes=True)


class TaskList(BaseModel):
    tasks: list[TaskPublic]


class FilterPage(BaseModel):
    offset: int = Field(ge=0, default=0)
    limit: int = Field(ge=0, default=10)


class TaskPage(FilterPage):
    title: str | None = Field(default=None, min_length=3)
    description: str | None = None
    state: TaskState | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3)
    description: str | None = None
    state: TaskState | None = None
