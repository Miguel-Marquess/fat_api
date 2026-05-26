from http import HTTPStatus


def test_token_acess(client, user):
    response_acess = client.post(
        '/auth/login',
        data={'username': user.email, 'password': user.clean_password},
    )  # como e formulario, passa data e nao json

    response_token = response_acess.json()

    assert response_acess.status_code == HTTPStatus.OK
    assert response_token['token_type'] == 'Bearer'
    assert 'access_token' in response_token


def test_login_not_authorized(client, user):
    response = client.post(
        '/auth/login',
        data={'username': user.email, 'password': 'wrongpassword'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Email or Password incorrect.'}
