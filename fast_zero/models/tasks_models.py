from enum import Enum


# enum cria quantidade finita de opcoes, se nao colocar uma delas
# e levantado erro 422
class TaskState(str, Enum):
    draft = 'draft'
    todo = 'todo'
    doing = 'doing'
    done = 'done'
    trash = 'trash'
