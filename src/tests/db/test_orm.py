from models.orm import BaseModel, syncdb, cleandb
from models.orm.types import Password
from sqlalchemy import Column, ForeignKey, Integer, String, Numeric, Boolean
from sqlalchemy.orm import relationship
from unittest.mock import patch
from app import get_or_create_app
from models.orm.connection import create_pool

import os


class User(BaseModel):
    __tablename__ = 'users'
    username = Column(String(64))
    password = Column(Password)
    email = Column(String(64))
    is_active = Column(Boolean(), nullable=False, default=False)
    credit_score = Column(Numeric(), nullable=True)

    def get_id(self):
        return self.id

    @classmethod
    def authenticate(cls, username=None, email=None, password=None):
        user = User.objects.get(username=username, email=email)
        assert user.password == password
        return user


class Genre(BaseModel):
    __tablename__ = 'genre'
    name = Column(String(256))
    description = Column(String(256))


class Artist(BaseModel):
    __tablename__ = 'artist'
    name = Column(String(256))
    description = Column(String(256))
    albums = relationship('Album', backref='artist')
    genre_id = Column(Integer, ForeignKey('genre.id'))


class Album(BaseModel):
    __tablename__ = 'album'
    name = Column(String(256))
    description = Column(String(256))
    artist_id = Column(Integer, ForeignKey('artist.id'))




mock_env = {
    'FLASK_CONFIG_PREFIXES': 'SQLALCHEMY',
    'SQLALCHEMY_DEFAULT': 'postgresql://ds:dsps@pgdb:5432/ds_test',
}

os_environ_mock = patch.dict(os.environ, mock_env)



def test_simple_insert():
    with os_environ_mock:
        app = get_or_create_app(__name__)
        with app.app_context():

            pool = create_pool()
            syncdb(pool=pool)
            cleandb(pool=pool)
            assert 0 == Genre.objects.count()
            genre = Genre(name='name1', description='dsc1')
            genre.add()
            pool.commit()
            assert 1 == Genre.objects.count()
            genre2 = Genre(name='name2', description='dsc2')
            genre2.add()
            genre2.objects.pool.commit()
            assert 2 == Genre.objects.count()

def test_multi_insert():
    with os_environ_mock:
        app = get_or_create_app(__name__)

        with app.app_context():
            pool = create_pool()
            syncdb(pool=pool)
            cleandb(pool=pool)

            assert 0 == Genre.objects.count()
            data = [
                Genre(
                    name='genre{}'.format(x),
                    description='descript{}'.format(x))
                for x in range(100)
            ]

            Genre.objects.add_all(data)
            pool.commit()
            assert 100 == Genre.objects.count()

def test_relationships():
    with os_environ_mock:
        app = get_or_create_app(__name__)
        with app.app_context():
            pool = create_pool()
            syncdb(pool=pool)
            cleandb(pool=pool)
            rock = Genre(name='Rock', description='rock yeah!!!')
            rock.add()
            pool.commit()
            pink = Artist(
                genre_id=rock.id, name='Pink Floyd', description='Awsome')
            pink.add()
            pool.commit()
            dark = Album(
                artist_id=pink.id, name='Dark side of the moon',
                description='Interesting')
            dark.add()
            pool.commit()
            rolling = Artist(
                genre_id=rock.id,
                name='Rolling Stones', description='Acceptable')

            rolling.add()
            pool.commit()

            hits = Album(
                artist_id=rolling.id, name='Greatest hits',
                description='Interesting')
            hits.add()
            pool.commit()
            assert 2 == Album.objects.count()

            wall = Album(
                artist_id=pink.id, name='The Wall',
                description='Interesting')
            wall.add()
            pool.commit()
            assert 2 == len(pink.albums)
            assert 2 == len(Artist.objects.filter_by(genre_id=rock.id)[:])

def test_update():
    with os_environ_mock:
        app = get_or_create_app(__name__)
        with app.app_context():
            pool = create_pool()
            syncdb(pool=pool)
            cleandb(pool=pool)
            rock = Genre(name='Rock', description='rock yeah!!!')
            rock.add()
            pool.commit()
            description_updated = 'description_updated'
            rock.description = description_updated
            rock.update()
            pool.commit()
            rock2 = Genre.objects.get(id=rock.id)
            assert rock2.description == description_updated
            assert 1 == Genre.objects.count()

def test_get_for_update():
    with os_environ_mock:
        app = get_or_create_app(__name__)
        with app.app_context():
            pool = create_pool()
            syncdb(pool=pool)
            cleandb(pool=pool)
            rock = Genre(name='Rock', description='rock yeah!!!')
            rock.add()
            pool.commit()
            rock2 = Genre.objects.get_for_update(id=rock.id)
            rock2.name = 'updated name'
            rock2.update()
            assert rock2.id == rock.id
            rock2.objects.pool.close()

def test_delete():
    with os_environ_mock:
        app = get_or_create_app(__name__)
        with app.app_context():
            pool = create_pool()
            syncdb(pool=pool)
            cleandb(pool=pool)
            rock = Genre(name='Rock', description='rock yeah!!!')
            rock.add()
            pool.commit()
            assert 1 == Genre.objects.count()
            rock.delete()
            pool.commit()
            assert 0 == Genre.objects.count()

def test_raw_sql():
    with os_environ_mock:
        app = get_or_create_app(__name__)
        with app.app_context():
            pool = create_pool()
            syncdb(pool=pool)
            cleandb(pool=pool)
            rock = Genre(name='Rock', description='rock yeah!!!')
            rock.add()
            pool.commit()
            pink = Artist(
                genre_id=rock.id, name='Pink Floyd', description='Awsome')
            pink.add()
            pool.commit()
            dark = Album(
                artist_id=pink.id, name='Dark side of the moon',
                description='Interesting')
            dark.add()
            pool.commit()
            rolling = Artist(
                genre_id=rock.id,
                name='Rolling Stones', description='Acceptable')

            rolling.add()
            pool.commit()
            sql = """
                SELECT a.name as artist_name, a.description artist_description,
                g.name as artist_genre
                FROM artist a
                INNER JOIN genre g ON a.genre_id = g.id
                ORDER BY a.id DESC;
            """

            result = Genre.objects.raw_sql(sql).fetchall()
            assert 2 == len(result)
            assert 'Rolling Stones' == result[0][0]

            sql = """
                SELECT a.name as artist_name, a.description artist_description,
                g.name as artist_genre
                FROM artist a
                INNER JOIN genre g ON a.genre_id = g.id
                WHERE a.id = :artist_id
                ORDER BY a.id DESC;
            """

            result = Genre.objects.raw_sql(sql, artist_id=pink.id).fetchall()
            assert 1 == len(result)
            assert 'Pink Floyd' == result[0][0]


def test_encrypted_password():
    with os_environ_mock:
        app = get_or_create_app(__name__)
        with app.app_context():
            pool = create_pool()
            syncdb(pool=pool)
            cleandb(pool=pool)
            user = User(
                username='username', email='eil@il.com', password='123')
            user.add()
            pool.commit()
            id = user.id
            # objects needs to dereferenciated otherwise
            # user2 will be just a copy of user
            user = None
            user2 = User.objects.get(id=id)
            assert id == user2.id
            assert '123' == user2.password
