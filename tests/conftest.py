from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import UserDataBase, registry_table


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,  # forca a engine a usar
        # a mesma conexao
    )
    registry_table.metadata.create_all(engine)
    with Session(engine) as ss:
        yield ss
    registry_table.metadata.drop_all(engine)
    engine.dispose()  # descarta engine


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


@pytest.fixture
def user(session):
    user_db = UserDataBase(
        username='testname',
        email='email@exemple.com',
        password='secret',
    )
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db
