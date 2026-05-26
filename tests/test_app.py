from http import HTTPStatus


def test_root_deve_retornarOlaMundo(client):

    response = client.get('/')

    # assert == garanta

    assert response.json() == {'message': 'Ola mundo!'}
    assert response.status_code == HTTPStatus.OK

    # json() pega o corpo da requisicao e compara com  == {} (literalmente)
