from dataclasses import asdict

from sqlalchemy import select

from fast_zero.models import UserDataBase


def test_create_user_db(session, mock_db_time):
    with mock_db_time(model=UserDataBase) as time:
        user = UserDataBase(
            username='Miguel', email='miguel@gmail.com', password='secret'
        )

        session.add(user)
        session.commit()

        user_db = session.scalar(
            select(UserDataBase).where(UserDataBase.username == 'Miguel')
        )
        assert asdict(user_db) == {  # aqui ja e o
            # obj modificado
            'id': 1,
            'username': 'Miguel',
            'email': 'miguel@gmail.com',
            'password': 'secret',
            'created_at': time,  # aqui recebe o time praq
            # possa fazer a verificacao, o obj time
            'updated_at': time,
        }
        # o id e 1 pois sempre o banco esta sendo apagadop(registry.drop_all())
