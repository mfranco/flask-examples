Flask Examples
=================

RESTFUL API endpoints built using Flask Framework (http://flask.pocoo.org/) and Sqlalchemy
(http://www.sqlalchemy.org/)

Requirements
------------
- Python 3
- Docker
- Docker-Compose


Installation
-------------

Create the docker environment with the following commands:

```
  cd dtools
  docker-compose up
```


Unit Tests
------------

Run the unit test suite with the following command:


```
python3 manage.py test --q src/

```


To run all the tests inside one file:


```
python3 manage.py test --q src/tests/test_app.py 
```


To run a specific test:


```
python3 manage.py test --q src/tests/test_app.py::test_app_config
```



SqlAlchemy ORM
-----------------

This project contains a very simple ORM built using SqlAlchemy (https://www.sqlalchemy.org/)

The following example shows how to create basic models:


```
from pg.types import Password
from sqlalchemy import Column, ForeignKey, Integer, String, Numeric, Boolean
from sqlalchemy.orm import relationship
from pg.orm import BaseModel



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


```


The following examples show how to perform basic insert operations



```

mock_env = {
    'FLASK_CONFIG_PREFIXES': 'SQLALCHEMY',
    'SQLALCHEMY_DEFAULT': 'postgresql://ds:dsps@pgdb:5432/ds_test',
}

os_environ_mock = patch.dict(os.environ, mock_env)


def test_simple_insert():
    with os_environ_mock:
        app = get_or_create_app(__name__)
        with app.app_context():
            db = init_db(app)
            db.syncdb()
            db.cleandb()
            assert 0 == Genre.objects.count()
            genre = Genre(name='name1', description='dsc1')
            genre.add()
            db.pool.commit()
            assert 1 == Genre.objects.count()
            genre2 = Genre(name='name2', description='dsc2')
            genre2.add()
            db.pool.commit()
            assert 2 == Genre.objects.count()


```



You can perform also multiple insert operations at once:


```
def test_multi_insert():
    with os_environ_mock:
        app = get_or_create_app(__name__)

        with app.app_context():
            db = init_db(app)
            db.syncdb()
            db.cleandb()

            assert 0 == Genre.objects.count()
            data = [
                Genre(
                    name='genre{}'.format(x),
                    description='descript{}'.format(x))
                for x in range(100)
            ]

            Genre.objects.add_all(data)
            db.pool.commit()
            assert 100 == Genre.objects.count()

```



The following example shows how to use foreing keys for relational data:


```
def test_relationships():
    with os_environ_mock:
        app = get_or_create_app(__name__)
        with app.app_context():
            db = init_db(app)
            db.syncdb()
            db.cleandb()
            rock = Genre(name='Rock', description='rock yeah!!!')
            rock.add()
            db.pool.commit()
            pink = Artist(
                genre_id=rock.id, name='Pink Floyd', description='Awsome')
            pink.add()
            db.pool.commit()
            dark = Album(
                artist_id=pink.id, name='Dark side of the moon',
                description='Interesting')
            dark.add()
            db.pool.commit()
            rolling = Artist(
                genre_id=rock.id,
                name='Rolling Stones', description='Acceptable')

            rolling.add()
            db.pool.commit()

            hits = Album(
                artist_id=rolling.id, name='Greatest hits',
                description='Interesting')
            hits.add()
            db.pool.commit()
            assert 2 == Album.objects.count()

            wall = Album(
                artist_id=pink.id, name='The Wall',
                description='Interesting')
            wall.add()
            db.pool.commit()
            assert 2 == len(pink.albums)
            assert 2 == len(Artist.objects.filter_by(genre_id=rock.id)[:])

```



Update operations are also supported:


```
def test_update():
    with os_environ_mock:
        app = get_or_create_app(__name__)
        with app.app_context():
            db = init_db(app)
            db.syncdb()
            db.cleandb()
            rock = Genre(name='Rock', description='rock yeah!!!')
            rock.add()
            db.pool.commit()
            description_updated = 'description_updated'
            rock.description = description_updated
            rock.update()
            db.pool.commit()
            rock2 = Genre.objects.get(id=rock.id)
            assert rock2.description == description_updated
            assert 1 == Genre.objects.count()

```



The *get_for_update* method is useful if you want to retrieve an object with lock for updates:


```
def test_get_for_update():
    with os_environ_mock:
        app = get_or_create_app(__name__)
        with app.app_context():
            db = init_db(app)
            db.syncdb()
            db.cleandb()
            rock = Genre(name='Rock', description='rock yeah!!!')
            rock.add()
            db.pool.commit()
            rock2 = Genre.objects.get_for_update(id=rock.id)
            rock2.name = 'updated name'
            rock2.update()
            assert rock2.id == rock.id
            rock2.objects.db.pool.close()


```


The following examples show how to delete records from the database:

```
def test_delete():
    with os_environ_mock:
        app = get_or_create_app(__name__)
        with app.app_context():
            db = init_db(app)
            db.syncdb()
            db.cleandb()
            rock = Genre(name='Rock', description='rock yeah!!!')
            rock.add()
            db.pool.commit()
            assert 1 == Genre.objects.count()
            rock.delete()
            db.pool.commit()
            assert 0 == Genre.objects.count()
```


The ORM supports the usage of raw SQL sentences:

```
def test_raw_sql():
    with os_environ_mock:
        app = get_or_create_app(__name__)
        with app.app_context():
            db = init_db(app)
            db.syncdb()
            db.cleandb()
            rock = Genre(name='Rock', description='rock yeah!!!')
            rock.add()
            db.pool.commit()
            pink = Artist(
                genre_id=rock.id, name='Pink Floyd', description='Awsome')
            pink.add()
            db.pool.commit()
            dark = Album(
                artist_id=pink.id, name='Dark side of the moon',
                description='Interesting')
            dark.add()
            db.pool.commit()
            rolling = Artist(
                genre_id=rock.id,
                name='Rolling Stones', description='Acceptable')

            rolling.add()
            db.pool.commit()
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
```




Application Configuration
------------------------------

This application translates enviroment variables to Flask configuration values. This approachs allows the usage of key value pairs tools
such as terraform vault (https://blog.backendhelpers.co/en/2019/vault-intro/index.html) for secret management. In order to tell Flask what
kind of enviroment variables to look for, all you need to do is to define the following variable:

```
export FLASK_CONFIG_PREFIXES="FLASK,SQLALCHEMY,AWS"
```


Flask will look for all variables with prefixes **FLASK** and **SQLALCHEMY**


```
export SQLALCHEMY_DEFAULT="postgresql://ds:dsps@pgdb:5432/ds_test"
export SQLALCHEMY_DB2="postgresql://ds:dsps@pgdb:5432/ds2_test"
export AWS_SECRET="s3cr3t"

```


The following unit tests examplains better how the configuration works:

```

def test_app_config():
    """
    Test if app loads configuration values from
    environmnet variables properly
    """
    mock_env = {
        'FLASK_CONFIG_PREFIXES': 'AWS,DB',
        'AWS_SECRET': 'S3CR3T',
        'DB_USERNAME': 'USER',
        'PREFIX_NOT_EXISTS': 'SHOULD_NOT_EXIST',
        'FLASK_BH_DEBUG_LEVEL': 'DEBUG'
    }

    os_environ_mock = patch.dict(os.environ, mock_env)

    with os_environ_mock:
        app = get_or_create_app(__name__)
        assert 'AWS_SECRET' in app.config
        assert 'DB_USERNAME' in app.config
        assert 'PREFIX_NOT_EXISTS' not in app.config

```





Json Serializers
-------------------


This project uses https://python-jsonschema.readthedocs.io/en/stable/ to handle json serialization and deserialization.

The following unit tests show the basic usage of this feature:


```

from serializers import JsonSerializer, SerializerError
from tests.base import BaseTestFactory

from datetime import date, datetime
from flask import json
from jsonschema.exceptions import ValidationError

import pytest


new_message_schema = {
    'type': 'object',
    'properties': {
        'title': {'type': 'string'},
        'body': {'type': 'string'},
        'date': {'type': 'string', 'format': 'date'},
        'date-time': {'type': 'string', 'format': 'date-time'}
    },
    'required': ['title', 'body', 'date', 'date-time']
}


message_schema = {
    'type': 'object',
    'definitions': {
        'new_message': new_message_schema
    },
    'allOf': [
        {'$ref': '#/definitions/new_message'},
        {
            'properties': {
                'key': {'type': 'string', 'format': 'uuid'}},
            'required': ['key']
        }
    ]
}


error_schema = {
    'type': 'object',
    'required': ['code', 'message'],
    'properties': {
        'code': {'type': 'integer', 'format': 'int32'},
        'message': {'type': 'string'}
    }
}


class NewMessage(JsonSerializer):
    _schema = new_message_schema


class Message(JsonSerializer):
    _schema = message_schema


class Error(JsonSerializer):
    _schema = error_schema


def test_basic_json_serializer():
    # basic validation for empty data
    with pytest.raises(SerializerError):
        serializer = Error(data={})

    data = {
        'code': 400,
        'message': BaseTestFactory.create_random_string()
    }

    serializer = Error(data=data)

    # checks that assign after initialization is not possible
    with pytest.raises(AttributeError):
        serializer.data = {}

    with pytest.raises(AttributeError):
        serializer.payload = None

    assert data == serializer.data
    payload = json.dumps(data, indent=4)
    assert payload == serializer.payload


def test_serializer_uuid_date_datetime():
    """
    Tests is serialization process don't modify original formats
    """
    data = {
        'title': BaseTestFactory.create_random_string(),
        'body': BaseTestFactory.create_random_string(),
        'date': date.today(),
        'date-time': datetime.utcnow()
    }

    serializer = NewMessage(data=data)

    assert serializer.data == data

    with pytest.raises(
            ValidationError, match=r"'key' is a required property"):

        Message(data=data)

    data['key'] = BaseTestFactory.create_random_uuid()

    serializer2 = Message(data=data)
    assert serializer2.data == data

```




Useful commands
-------------------


### Kill all running docker containers:


 docker kill $(docker ps | grep pg | awk '{print $1}')
    


See also
---------
[Flask Framework Website](http://flask.pocoo.org)

[Flask python3 support](http://flask.pocoo.org/docs/python3/)

[Sqlalchemy Website](http://www.sqlalchemy.org/)

[Designing a RESTful API with Python and Flask](http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask)

[Unit testing framework](http://docs.python.org/2/library/unittest.html)

[argparse — Parser for command-line options, arguments and sub-commands](http://docs.python.org/dev/library/argparse.html)

[Python @property versus getters and setters](http://stackoverflow.com/questions/6618002/python-property-versus-getters-and-setters)
