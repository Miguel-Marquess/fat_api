from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from fast_zero.dependencies import Current_user, OAuth2Form, T_Session
from fast_zero.models.db_models import UserDataBase
from fast_zero.schemas.users_schemas import Token
from fast_zero.security import (
    create_acess_token,
    verify_password,
)

router = APIRouter(tags=['auth'], prefix='/auth')


@router.post('/login', response_model=Token)
async def login_for_acess_token(
    form_data: OAuth2Form,
    # usa a propria classe como dependency,
    # e o OAuth2 tem dependencia propria
    # ela foi feita para ser assim mesmo
    session: T_Session,
):
    user = await session.scalar(
        select(UserDataBase).where(UserDataBase.email == form_data.username)
    )

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=400,
            detail='Email or Password incorrect.',
        )

    token = create_acess_token(claims={'sub': user.email})
    return {'access_token': token, 'token_type': 'Bearer'}


@router.post('/refresh_token', response_model=Token)
async def refresh_access_token(user: Current_user):
    # o refresh token deve ser enviado em conjunto com o token no login
    # para que o um novo token seja gerado somente se o refresh token
    # e valido tambem
    # exemplo: access_token = 30min
    # refresh = 7 dias
    new_access_token = create_acess_token(claims={'sub': user.email})

    return {'access_token': new_access_token, 'token_type': 'Bearer'}
