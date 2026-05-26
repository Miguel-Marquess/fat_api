from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_get_users(client, user, token):
    user_schema = UserPublic.model_validate(user).model_dump()
    # model validate transforma
    # outros obj em obj pydantic
    # dentro do schema, deve ter model_config
    # ve la
    response = client.get(
        '/users/', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}
    # validation with pydantic


def test_get_unique_user_should_return_404(client, token):
    response = client.get(
        '/users/0', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User Not Found'}


def test_get_unique_user(client, user, token):
    response = client.get(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )

    user_schema = UserPublic.model_validate(user).model_dump()
    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema
