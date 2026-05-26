from http import HTTPStatus

from jwt import decode

from fast_zero.security import create_acess_token


def test_jwt(settings):
    claims = {'test': 'test'}

    token = create_acess_token(claims)
    decoded = decode(token, settings.SECRET_KEY, settings.ALGORITHM)

    assert decoded['test'] == claims['test']
    assert 'exp' in decoded


def test_invalid_jwt(client):
    response = client.put(
        '/users/1', headers={'Authorization': 'Bearer invalid-token'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Credentials cannot be validateds'}


def test_invalid_sub_email(client):
    claims = {'test': 'test'}
    token = create_acess_token(claims)

    response = client.get(
        '/users', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Credentials cannot be validateds'}


def test_user_not_valid(client):
    claims = {'sub': 'test'}
    token = create_acess_token(claims)

    response = client.get(
        '/users', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Credentials cannot be validateds'}
