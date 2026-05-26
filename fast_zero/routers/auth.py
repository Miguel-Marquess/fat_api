from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import UserDataBase
from fast_zero.schemas import Token
from fast_zero.security import (
    create_acess_token,
    verify_password,
)

router = APIRouter(tags=['auth'], prefix='/auth')
T_Session = Annotated[Session, Depends(get_session)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/login', response_model=Token)
def login_for_acess_token(
    form_data: OAuth2Form,
    # usa a propria classe como dependency,
    # e o OAuth2 tem dependencia propria
    # ela foi feita para ser assim mesmo
    session: T_Session,
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
