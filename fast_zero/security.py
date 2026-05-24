import secrets
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import decode, encode
from jwt.exceptions import DecodeError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import UserDataBase

pwd_context = PasswordHash.recommended()
# constantes
SECRET_KEY = secrets.token_hex()
ALGORITHM = 'HS256'
ACESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


# coloca a rota que e usada para autenticacao
# se o user nao tiver um token bearer, ele e enviado para
# essa rota


# Se vc ta deslogado, vc consegue logar pelo Authorize
# e ele carrega a rota <login>, que foi a colocada
# no tokenUrl.
def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(pure_password: str, hashed_password: str):
    return pwd_context.verify(pure_password, hashed_password)


def create_acess_token(claims: dict):
    to_encode = claims.copy()
    # copia para nao alterar o data org

    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=ACESS_TOKEN_EXPIRE_MINUTES
    )
    # pega horario atual, soma 30 minutos
    # o timeldelta e um objeto que soma
    # e subtrai datas e horarios
    to_encode.update({'exp': expire})
    # update atualiza mais de um campo por vez
    encoded_jwt = encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt


def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme),
    # scheme extrai o token
):
    invalid_credentials = HTTPException(
        status_code=401,
        detail='Credentials cannot be validateds',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = decode(token, SECRET_KEY, ALGORITHM)
        sub_email = payload.get('sub')
        if not sub_email:
            raise invalid_credentials
    except DecodeError:
        raise invalid_credentials

    user = session.scalar(
        select(UserDataBase).where(UserDataBase.email == sub_email)
    )

    if not user:
        raise invalid_credentials
    return user
