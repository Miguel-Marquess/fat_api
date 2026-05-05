from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_zero.app import app

client = TestClient(app)


def test_root_deve_retornarOlaMundo():
    response = client.get('/')

    # assert == garanta

    assert response.json() == {'message': 'Ola mundo!'}
    assert response.status_code() == HTTPStatus.OK

    # json() pega o corpo da requisicao e compara com  == {} (literalmente)
