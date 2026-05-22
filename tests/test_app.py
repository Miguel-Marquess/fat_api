from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_root_deve_retornarOlaMundo(client):

    response = client.get('/')

    # assert == garanta

    assert response.json() == {'message': 'Ola mundo!'}
    assert response.status_code == HTTPStatus.OK

    # json() pega o corpo da requisicao e compara com  == {} (literalmente)


def test_create_user(client):

    response = client.post(
        '/users/',
        json={
            'username': 'testname',
            'password': 'secret',
            'email': 'email@exemple.com',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'testname',
        'email': 'email@exemple.com',
        'id': 1,
    }


def test_create_user_should_return_409(client, user):
    response_created = client.post(
        '/users',
        json={
            'username': 'testname',
            'password': 'secret',
            'email': 'email@exemple.com',
        },
    )

    assert response_created.status_code == HTTPStatus.CONFLICT
    assert response_created.json() == {
        'detail': 'Email or Username already exist.'
    }


def test_get_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    # model validate transforma
    # outros obj em obj pydantic
    # dentro do schema, deve ter model_config
    # ve la
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}
    # validation with pydantic


def test_no_get_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_get_unique_user_should_return_404(client):
    response = client.get('/users/0')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User Not Found'}


def test_get_unique_user(client, user):
    response = client.get('/users/1')

    user_schema = UserPublic.model_validate(user).model_dump()
    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


def test_update_user(client, user):
    # user e um objeto ORM conectado
    # a session
    response = client.put(
        '/users/1',
        json={
            'username': 'updated_user',
            'email': 'updated_user@exemple.com',
            'password': 'newpasswordupdated',
        },
    )
    # essa funcao pega o estado atual de <user>
    user_schema = UserPublic.model_validate(user).model_dump()
    # o SQLAlchemy mantém o objeto ORM sincronizado
    # na mesma session, e o refresh recarrega os dados
    # do banco para o objeto
    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


def test_update_integrity_error(client, user):
    client.post(  # cria novo user para
        # dar conflito
        '/users',
        json={
            'username': 'pingueleto',
            'email': 'pingueleto@exemple.com',
            'password': 'secret',
        },
    )

    response_update = client.put(
        f'/users/{user.id}',
        json={  # conflito por username
            'username': 'pingueleto',
            'email': 'email@exemple.com',
            'password': 'newpassword',
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'Username or Email already exist.'
    }


def test_update_user_should_return_404(client):
    response = client.put(
        'users/0',
        json={
            'username': 'testname',
            'email': 'email@exemple.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User Not Found'}


def test_delete_user(client, user):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User was deleted.'}


def test_delete_user_should_return_404(client):
    response = client.delete('/users/0')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User Not Found'}
