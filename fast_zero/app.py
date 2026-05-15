from fastapi import FastAPI, HTTPException

from fast_zero.schemas import Message, User, UserDB, UserList, UserPublic

app = FastAPI()

database = []

# breakpoint() -> muito importante


@app.get('/', status_code=200, response_model=Message)
def read_root():
    return {'message': 'Ola mundo!'}


@app.post('/users/', status_code=201, response_model=UserPublic)
# o proprio pydantic
# valida a saida de dados, automaticamente ele
# coloca o valor retornado no response model
def create_user(user: User):
    user_with_id = UserDB(**user.model_dump(), id=len(database) + 1)
    database.append(user_with_id)
    return user_with_id  # nao retorna com a senha devido


# ao response_model=UserPublic.


@app.get('/users/', status_code=200, response_model=UserList)
def get_users():
    return {'users': database}


@app.get('/users/{user_id}', status_code=200, response_model=UserPublic)
def get_unique_user(user_id: int):
    if 1 <= user_id <= len(database):
        return database[user_id - 1]
    raise HTTPException(status_code=404, detail='User Not Found')


@app.put('/users/{user_id}', status_code=200, response_model=UserPublic)
# path parameter pega da URL
# e o user do body
def update_user(user_id: int, user: User):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(status_code=404, detail='User Not Found')
    user_with_id = UserDB(**user.model_dump(), id=user_id)
    database[user_id - 1] = user_with_id
    return user_with_id


@app.delete('/users/{user_id}', status_code=200, response_model=UserPublic)
def delete_user(user_id: int):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(status_code=404, detail='User Not Found')
    return database.pop(user_id - 1)
