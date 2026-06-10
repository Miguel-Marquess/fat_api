from http import HTTPStatus

from fast_zero.schemas.users_schemas import UserPublic


def test_update_user(client, user, token):
    # user e um objeto ORM conectado
    # a session
    response = client.put(
        '/users/1',
        json={
            'username': 'updated_user',
            'email': 'updated_user@exemple.com',
            'password': 'newpasswordupdated',
        },
        headers={'Authorization': f'Bearer {token}'},
    )
    # essa funcao pega o estado atual de <user>
    user_schema = UserPublic.model_validate(user).model_dump()
    # o SQLAlchemy mantém o objeto ORM sincronizado
    # na mesma session, e o refresh recarrega os dados
    # do banco para o objeto
    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


def test_update_integrity_error(client, user, other_user, token):
    response_update = client.put(
        f'/users/{user.id}',
        json={  # conflito por username
            'username': other_user.username,
            'email': 'email@exemple.com',
            'password': 'newpassword',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'Username or Email already exist.'
    }


def test_update_user_forbidden(client, other_user, token):
    # a fixture other_client garante que um usuario nao pode
    # mexer nos dados de outro que ESTEJA na base de dados.
    response = client.put(
        f'/users/{other_user.id}',
        json={
            'username': 'updated_user',
            'email': 'updated_user@exemple.com',
            'password': 'newpasswordupdated',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions. Forbidden!'}
