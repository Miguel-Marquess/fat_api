from http import HTTPStatus


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
