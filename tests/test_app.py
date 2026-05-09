from http import HTTPStatus


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
            'username': 'Miguel',
            'password': 'secret',
            'email': 'email@exemple.com',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'Miguel',
        'email': 'email@exemple.com',
        'id': 1,
    }


def test_get_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'username': 'Miguel',
                'email': 'email@exemple.com',
                'id': 1,
            },
        ]
    }


def test_update_user(client):
    response = client.put(
        '/users/1',
        json={
            'username': 'Miguel',
            'email': 'email@exemple.com',
            'password': 'secret',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'Miguel',
        'email': 'email@exemple.com',
        'id': 1,
    }


def test_delete_user(client):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'Miguel',
        'email': 'email@exemple.com',
        'id': 1,
    }
