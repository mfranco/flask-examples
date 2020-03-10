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
python3 manage.py test --q src/tests/
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
from models.orm import BaseModel
from models.orm.types import Password
from sqlalchemy import Column, ForeignKey, Integer, String, Numeric, Boolean
from sqlalchemy.orm import relationship


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

assert 0 == Genre.objects.count()
genre = Genre(name='name1', description='dsc1')
genre.add()
genre.objects.pool.commit()
assert 1 == Genre.objects.count()
genre2 = Genre(name='name2', description='dsc2')
genre2.add()
genre2.objects.pool.commit()
assert 2 == Genre.objects.count()


```



You can perform also multiple insert operations at once:


```
assert 0 == Genre.objects.count()
data = [
    Genre(
        name='genre{}'.format(x),
        description='descript{}'.format(x))
    for x in range(100)
]

Genre.objects.add_all(data)
Genre.objects.pool.commit()
assert 100 == Genre.objects.count()

```



The following example shows how to use foreing keys for relational data:


```
rock = Genre(name='Rock', description='rock yeah!!!')
rock.add()
rock.objectrs.pool.commit()
pink = Artist(
    genre_id=rock.id, name='Pink Floyd', description='Awsome')
pink.add()
pink.objects.pool.commit()
dark = Album(
    artist_id=pink.id, name='Dark side of the moon',
    description='Interesting')
dark.add()
dark.objects.pool.commit()
rolling = Artist(
    genre_id=rock.id,
    name='Rolling Stones', description='Acceptable')

rolling.add()
rolling.objects.pool.commit()

hits = Album(
    artist_id=rolling.id, name='Greatest hits',
    description='Interesting')
hits.add()
hits.objects.pool.commit()
assert 2 == Album.objects.count()

wall = Album(
    artist_id=pink.id, name='The Wall',
    description='Interesting')
wall.add()
wall.objects.pool.commit()
assert 2 == len(pink.albums)
assert 2 == len(Artist.objects.filter_by(genre_id=rock.id)[:])

```



Update operations are also supported:


```
rock = Genre(name='Rock', description='rock yeah!!!')
rock.add()
rocke.objects.pool.commit()
description_updated = 'description_updated'
rock.description = description_updated
rock.update()
rock.objects.pool.commit()
rock2 = Genre.objects.get(id=rock.id)
assert rock2.description == description_updated
assert 1 == Genre.objects.count()

```



The *get_for_update* mehthod is useful if you want to retrieve an object with lock for updates:


```
rock = Genre(name='Rock', description='rock yeah!!!')
rock.add()
pool.commit()
rock2 = Genre.objects.get_for_update(id=rock.id)
rock2.name = 'updated name'
rock2.update()
assert rock2.id == rock.id
rock2.objects.pool.close()


```


The following examples show how to delete records from the database:

```
rock = Genre(name='Rock', description='rock yeah!!!')
rock.add()
rock.objects.pool.commit()
assert 1 == Genre.objects.count()
rock.delete()
rock.objects.pool.commit()
assert 0 == Genre.objects.count()
```


The ORM supports the usage of raw SQL sentences:

```
rock = Genre(name='Rock', description='rock yeah!!!')
rock.add()
pool.commit()
pink = Artist(
    genre_id=rock.id, name='Pink Floyd', description='Awsome')
pink.add()
pink.objects.pool.commit()
dark = Album(
    artist_id=pink.id, name='Dark side of the moon',
    description='Interesting')
dark.add()
dark.objects.pool.commit()
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


HTTP Views
---------------


User API
----------

The main goal is desing and built a RestFull API that handles user registration and login for a new service 
(let's say a music service but could be anything). The API format will be JSON. The first thing that we must do
is define a root url: ::

    http://[hostname]/mymusic/api/v1.0/


After that we will define the User Resource urls that will allows to create, query, update, delete an user.


Create an User
--------------

POST request to create an user: ::

    curl -X POST localhost:5000/mymusic/api/v1.0/users/ -H "Content-Type: application/json" \
         -d '{"username": "maigfrga", "email": "maigfrga@gmail.com", \
              "last_name": "franco", "first_name": "manuel"}'



This request will return a json with the user information, access_token included: ::

        {
          "user": {
            "access_token": "dda568fe6781259a1f9b910c6704b4da", 
            "email": "maigfrga@gmail.com", 
            "first_name": "manuel", 
            "id": 1, 
            "last_name": "franco", 
            "username": "maigfrga"
          }
        }



Authentication
--------------

GET, PUT, DELETE request requires authentication, the API expects two headers **api_access_token** and **api_username** the next example will return user information, authentication is required: ::


    curl  localhost:5000/mymusic/api/v1.0/users/ -H "api_access_token: dda568fe6781259a1f9b910c6704b4da" \
         -H "api_username: maigfrga"


This call will return the user data: ::

    {
        "access_token": "dda568fe6781259a1f9b910c6704b4da", 
        "email": "maigfrga@gmail.com", 
        "first_name": "manuel", 
        "id": 1, 
        "last_name": "franco", 
        "username": "maigfrga"
    }





Update an user
--------------

Perform a PUT request will update the user resource: ::


        curl -X PUT  localhost:5000/mymusic/api/v1.0/users/ -H "Content-Type: application/json" \
             -H "api_access_token: dda568fe6781259a1f9b910c6704b4da" \
             -H "api_username: maigfrga" -d '{"last_name": "last name modified"}'



Delete an user
--------------

Perform  a DELETE request will delete the user resource: ::

        curl -X DELETE  localhost:5000/mymusic/api/v1.0/users/  \
         -H "api_access_token: dda568fe6781259a1f9b910c6704b4da" \
         -H "api_username: maigfrga"


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
