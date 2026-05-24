from http import HTTPStatus

from jwt import decode

from fast_zero.security import ALGORITHM, SECRET_KEY, create_acess_token


def test_jwt():
    claims = {'test': 'test'}

    token = create_acess_token(claims)
    decoded = decode(token, SECRET_KEY, ALGORITHM)

    assert decoded['test'] == claims['test']
    assert 'exp' in decoded


def test_invalid_jwt(client):
    response = client.put(
        '/users/1', headers={'Authorization': 'Bearer invalid-token'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Credentials cannot be validateds'}
