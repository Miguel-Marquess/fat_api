from http import HTTPStatus

from freezegun import freeze_time


def test_token_acess(client, user):
    response_acess = client.post(
        '/auth/login',
        data={'username': user.email, 'password': user.clean_password},
    )  # como e formulario, passa data e nao json

    response_token = response_acess.json()

    assert response_acess.status_code == HTTPStatus.OK
    assert response_token['token_type'] == 'Bearer'
    assert 'access_token' in response_token


def test_login_wrong_password(client, user):
    response = client.post(
        '/auth/login',
        data={'username': user.email, 'password': 'wrongpassword'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Email or Password incorrect.'}


def test_login_wrong_email(client, user):
    response = client.post(
        '/auth/login',
        data={
            'username': 'wrong@exemple.com',
            'password': user.clean_password,
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Email or Password incorrect.'}


def test_should_expire_acess_token(client, user):
    with freeze_time('2026-12-31 00:00:00'):
        response = client.post(
            '/auth/login',
            data={'username': user.email, 'password': user.clean_password},
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']
        # o token vai ter a data do freeze_time

    with freeze_time('2026-12-31 00:32:00'):
        # aqui o token vai estar expirado, acessando 30min na frente
        response = client.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'wrongupdate',
                'email': 'wrongupdate@exemple.com',
                'password': 'wrongsecret',
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {
            'detail': 'Credentials cannot be validateds'
        }


def test_refresh_token(client, token):
    response = client.post(
        '/auth/refresh_token', headers={'Authorization': f'Bearer {token}'}
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'Bearer'


def test_refresh_expired_token(client, user):
    with freeze_time('2026-12-31 00:00:00'):
        response = client.post(
            '/auth/login',
            data={'username': user.email, 'password': user.clean_password},
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2026-12-31 00:32:00'):
        response = client.post(
            '/auth/refresh_token', headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {
            'detail': 'Credentials cannot be validateds'
        }
    # tenta decodar, e criar um novo access_token pelo o token antigo
    # mas o decode da errado pois o token antigo esta expirado.