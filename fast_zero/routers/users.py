from fastapi import (  # Injecao de dependencias,
    APIRouter,
    HTTPException,
)

# uma ex: ROTA que precisa de certa coisa para funcionar
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from fast_zero.database import get_user_by_id
from fast_zero.dependencies import Current_user, T_FilterPage, T_Session
from fast_zero.models import UserDataBase
from fast_zero.schemas import Message, User, UserList, UserPublic
from fast_zero.security import (
    get_password_hash,
)

router = APIRouter(tags=['users'], prefix='/users')
# tags = documentacao, 'menu' as rotas
# prefix = como todas as rotas tem /users, ele ajuda
# a nao repetrir, permitindo colocar somente /, nao
# precisando botar '[/users]' em todas as rotas


@router.post('/', status_code=201, response_model=UserPublic)
# o proprio pydantic
# valida a saida de dados, automaticamente ele
# coloca o valor retornado no response model
async def create_user(user: User, session: T_Session):
    # roda a funcao get session e passa seu resultado
    # para a funcao
    # 1. request chega
    # 2. FastAPI vê:
    # Depends(get_session)
    # 3. FastAPI executa get_session()
    # 4. entra no with Session(...)
    # 5. yield entrega a sessão
    # 6. rota usa a sessão
    # 7. rota termina
    # 8. FastAPI continua o generator
    # 9. sai do with
    # 10. sessão fecha automaticamente
    db_user = await session.scalar(
        select(UserDataBase).where(
            (UserDataBase.email == user.email)
            | (UserDataBase.username == user.username)
        )
    )
    if db_user:
        raise HTTPException(409, detail='Email or Username already exist.')
    db_user = UserDataBase(
        **user.model_dump(exclude={'password'}),
        password=get_password_hash(user.password),
        # passa manualmente pro UserDataBase
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@router.put('/{user_id}', status_code=200, response_model=UserPublic)
# path parameter pega da URL
# e o user do body
async def update_user(
    user_id: int,
    user: User,
    session: T_Session,
    current_user: Current_user,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403, detail='Not enough permissions. Forbidden!'
        )

    try:
        await session.execute(
            update(UserDataBase)
            .where(UserDataBase.id == user_id)
            .values(
                **user.model_dump(exclude={'password'}),
                password=get_password_hash(user.password),
            )
        )
        await session.commit()
        await session.refresh(current_user)
    except IntegrityError:
        raise HTTPException(
            status_code=409, detail='Username or Email already exist.'
        )
    return current_user


@router.delete('/{user_id}', status_code=200, response_model=Message)
async def delete_user(
    user_id: int,
    session: T_Session,
    current_user: Current_user,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403, detail='Not enough permissions. Forbidden!'
        )
    await session.delete(current_user)
    await session.commit()
    return {'message': 'User was deleted.'}


@router.get('/', status_code=200, response_model=UserList)
async def get_users(
    session: T_Session,
    current_user: Current_user,
    filter_page: T_FilterPage,
):
    users = await session.scalars(
        select(UserDataBase)
        .limit(filter_page.limit)
        .offset(filter_page.offset)
    )
    return {'users': users.fetchall()}


@router.get('/{user_id}', status_code=200, response_model=UserPublic)
async def get_unique_user(
    user_id: int,
    session: T_Session,
    current_user: Current_user,
):
    user_db = await get_user_by_id(user_id, session)
    # get_uset_by_id e uma funcao async, ou seja corrotine
    # ela precisa sere aguardada, pois retorna um obj coroutine
    if not user_db:
        raise HTTPException(status_code=404, detail='User Not Found')
    return user_db
