from contextlib import contextmanager
from datetime import datetime

import factory
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import UserDataBase, registry_table
from fast_zero.security import get_password_hash
from fast_zero.settings import Settings


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,  # forca a engine a usar
        # a mesma conexao, sqlite cria um banco novo a
        # cada sessao
    )
    async with engine.begin() as conn:
        await conn.run_sync(registry_table.metadata.create_all)
        # rodar banco de forma assincrona pode virar caos
        # criar tabela, apagar, remover registro
        # e melhor um de cada.
    async with AsyncSession(engine, expire_on_commit=False) as ss:
        yield ss
    async with engine.begin() as conn:
        await conn.run_sync(registry_table.metadata.drop_all)
        # tambem e porque o sqlalchemy e ddl sao sync e tao em um
        # ambiente async
    await engine.dispose()  # descarta engine


# funcao para 'ouvir' acoes para que realize algo antes de
# inserir um registro no banco, dando para 'roubar' nos testes


@contextmanager  # isso cria
# uma conexao with, q abre e fecha
def _mock_db_time(model, time=datetime(2026, 6, 11)):
    # mapper do ORM - conexao - objeto
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_hook)
    # Antes de inserir um objeto dessa classe,
    # execute essa funcao
    # isso é um callback
    yield time  # valor que vai para o as
    # caracteristica do contextmanager
    event.remove(model, 'before_insert', fake_time_hook)
    # remove e insere no banco com o func.now(),
    # pois ocorre tudo isso antes de inserir


@pytest.fixture
def mock_db_time():
    return _mock_db_time
    # isso retorna o OBJETO FUNCAO
    # pois NAO TEM PARENTESES


# mock_dc_time(User) ->
# isso executa a fixture python, e retorna
# _mock_db_time, e depois 'junta' o (User)
# ficando _mock_db_time(User)
# Pois o pytest quando chama uma fixture,
# automaticamente aquela fixture vira o valor retornado


@pytest_asyncio.fixture
async def user(session):
    password = 'secret'

    user_db = UserFactory(password=get_password_hash(password))
    # cria user randomizado a cada chamada

    session.add(user_db)
    await session.commit()
    await session.refresh(user_db)

    user_db.clean_password = password
    # new attribute! You can do this
    # in Python because objs are
    # dinamics, they have __dict__,
    # que guarda atributos dinamicamente
    # Nao guarda no banco, e um atributo
    # python temporario.
    return user_db


@pytest_asyncio.fixture
async def other_user(session):
    password = 'secret'

    user_db = UserFactory(password=get_password_hash(password))

    session.add(user_db)
    await session.commit()
    await session.refresh(user_db)

    user_db.clean_password = password
    return user_db


@pytest.fixture
def token(client, user):
    # o pytest chama a fixture uma vez por test
    # e reutiliza o resultado para outras chamadas
    response = client.post(
        '/auth/login',
        data={'username': user.email, 'password': user.clean_password},
    )

    return response.json()['access_token']


@pytest.fixture
def settings():
    return Settings()


class UserFactory(factory.Factory):
    class Meta:
        model = UserDataBase
        # vai criar uma nova classe UserDB

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@exemple.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}secret')
