from fastapi import FastAPI

from fast_zero.routers import auth, todo, users
from fast_zero.schemas.users_schemas import Message

app = FastAPI()
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(todo.router)


@app.get('/', status_code=200, response_model=Message)
async def read_root():
    return {'message': 'Ola mundo!'}
