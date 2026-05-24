from fastapi import (  # Injecao de dependencias,
    Depends,
    FastAPI,
    HTTPException,
)
from fastapi.security import OAuth2PasswordRequestForm

# uma ex: ROTA que precisa de certa coisa para funcionar
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_zero.database import get_session, get_user_by_id
from fast_zero.models import UserDataBase
from fast_zero.schemas import Message, Token, User, UserList, UserPublic
from fast_zero.security import (
    create_acess_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

app = FastAPI()


@app.get('/', status_code=200, response_model=Message)
def read_root():
    return {'message': 'Ola mundo!'}


@app.post('/users/', status_code=201, response_model=UserPublic)
# o proprio pydantic
# valida a saida de dados, automaticamente ele
# coloca o valor retornado no response model
def create_user(user: User, session=Depends(get_session)):
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
    db_user = session.scalar(
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
    session.commit()
    session.refresh(db_user)
    return db_user


@app.get('/users/', status_code=200, response_model=UserList)
def get_users(
    session=Depends(get_session),
    limit: int = 1,
    offset: int = 0,
    current_user=Depends(get_current_user),  # precisa ter um user logado
):  # o yield so retorna um generator
    # object, o Dependes faz toda essa dependencia
    # abrindo e fechando a conexao
    # ai a rota so preicsa executar
    # o dependes so recebe o objeto funcao
    # ele mesmo executa
    users = session.scalars(select(UserDataBase).limit(limit).offset(offset))
    return {'users': users.fetchall()}


@app.get('/users/{user_id}', status_code=200, response_model=UserPublic)
def get_unique_user(user_id: int, session=Depends(get_session)):
    user_db = get_user_by_id(user_id, session)
    if not user_db:
        raise HTTPException(status_code=404, detail='User Not Found')
    return user_db


@app.put('/users/{user_id}', status_code=200, response_model=UserPublic)
# path parameter pega da URL
# e o user do body
def update_user(
    user_id: int,
    user: User,
    session: Session = Depends(get_session),
    current_user: UserDataBase = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403, detail='Not enough permissions. Forbidden!'
        )

    try:
        session.execute(
            update(UserDataBase)
            .where(UserDataBase.id == user_id)
            .values(
                **user.model_dump(exclude={'password'}),
                password=get_password_hash(user.password),
            )
        )
        session.commit()
        session.refresh(current_user)
    except IntegrityError:
        raise HTTPException(
            status_code=409, detail='Username or Email already exist.'
        )
    return current_user


@app.delete('/users/{user_id}', status_code=200, response_model=Message)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: UserDataBase = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=401, detail='Not enough permissions. Forbidden!'
        )
    session.delete(current_user)
    session.commit()
    return {'message': 'User was deleted.'}


@app.post('/login', response_model=Token)
def login_for_acess_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    # usa a propria classe como dependency,
    # e o OAuth2 tem dependencia propria
    # ela foi feita para ser assim mesmo
    session: Session = Depends(get_session),
):
    user = session.scalar(
        select(UserDataBase).where(UserDataBase.email == form_data.username)
    )

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=401,
            detail='Email or Password incorrect.',
        )

    token = create_acess_token(claims={'sub': user.email})
    return {'access_token': token, 'token_type': 'Bearer'}
