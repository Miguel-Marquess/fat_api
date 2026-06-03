from http import HTTPStatus

from tests.conftest import UserFactory


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
    other_user = UserFactory(username=user.username, email=user.email)
    response_created = client.post(
        '/users',
        json={
            'username': other_user.username,
            'password': 'secret',
            'email': other_user.email,
        },
    )

    assert response_created.status_code == HTTPStatus.CONFLICT
    assert response_created.json() == {
        'detail': 'Email or Username already exist.'
    }
