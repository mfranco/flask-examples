from flask import json, request, Response, current_app
from app import get_or_create_app
from serializers import JsonSerializer
from views import json_response, BaseResourceView, SQLAlchemyView
from tests.base import BaseTestFactory
from models.orm import BaseModel, syncdb, cleandb
from sqlalchemy import Column, String
from datetime import date, datetime
from jsonschema.exceptions import ValidationError
from unittest.mock import patch
from models.orm.connection import create_pool

import os
import uuid


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


class MessageView(BaseResourceView):
    db = {
        'f3f99fe6-3099-4fc4-aad4-31babad961c6':
            {
                'key': 'f3f99fe6-3099-4fc4-aad4-31babad961c6',
                'title': 'title-1',
                'body': 'body-1',
                'date': date.today(),
                'date-time': datetime.utcnow()
            },

        'c7b20c35-2779-49ec-9d09-9e287fcbe372':
            {
                'key': 'c7b20c35-2779-49ec-9d09-9e287fcbe372',
                'title': 'title-2',
                'body': 'body-2',
                'date': date.today(),
                'date-time': datetime.utcnow()
            },
    }

    def get(self, key: uuid = None) -> Response:
        status = 200
        data = {}

        if key is not None:
            if key in self.db:
                data = Message(data=self.db[key]).data
            else:
                status = 404
        else:
            data = [
                Message(data=record).data
                for record in self.db.values()
            ]
        return json_response(status=status, data=data)

    def post(self) -> Response:
        app = current_app._get_current_object()
        try:
            serializer = NewMessage(data=request.json)
            data = serializer.data
            data['key'] = uuid.uuid4()
            return json_response(status=201, data=Message(data=data).data)

        except ValidationError as e:
            return json_response(status=400, data={'msg': e.message})

        except Exception as e:
            app.logger.error(e)
            return json_response(status=500)

    def put(self, key: uuid = None) -> Response:
        app = current_app._get_current_object()
        try:
            self.db[str(key)]
            serializer = Message(data=request.json)
            return json_response(status=200, data=serializer.data)

        except ValidationError as e:
            return json_response(status=400, data={'msg': e.message})

        except KeyError:
            return json_response(status=404)

        except Exception as e:
            app.logger.error(e)
            return json_response(status=500)


class BookSerializer(JsonSerializer):
    _schema = {
        'type': 'object',
        'properties': {
            'title': {'type': 'string'},
        },
        'required': ['title']
    }


class BookModel(BaseModel):
    __tablename__ = 'books'
    title = Column(String(256))


class BookSQLView(SQLAlchemyView):
    def post(self) -> Response:
        app = current_app._get_current_object()
        try:
            serializer = BookSerializer(data=request.json)
            data = serializer.data
            obj = BookModel(title=data['title'])
            obj.add()
            obj.objects.pool.commit()
            data['key'] = uuid.uuid4()
            return json_response(
                status=201, data=BookSerializer(data=data).data)

        except ValidationError as e:
            return json_response(status=400, data={'msg': e.message})

        except Exception as e:
            app.logger.error(e)
            return json_response(status=500)


ROUTES = (
    {
        'rule': '/messages', 'endpoint': 'messages',
        'view_func': MessageView.as_view('messages')
    },
    {
        'rule': '/messages/<uuid:key>', 'endpoint': 'home_key',
        'view_func': MessageView.as_view('messages_key')
    },
    {
        'rule': '/books', 'endpoint': 'books',
        'view_func': BookSQLView.as_view('books')
    },
)


MOCK_ENV = {
    'FLASK_CONFIG_PREFIXES': 'SQLALCHEMY',
    'SQLALCHEMY_DEFAULT': 'postgresql://ds:dsps@pgdb:5432/ds_test',
}

OS_ENVIRON_MOCK = patch.dict(os.environ, MOCK_ENV)


def test_http_get():
    with OS_ENVIRON_MOCK:
        get_or_create_app(__name__, ROUTES)
        view = MessageView()
        result = view.get()
        assert 200 == result.status_code
        j_content = json.loads(result.get_data().decode('utf-8'))
        assert 2 == len(j_content)


def test_http_post_method_view():
    with OS_ENVIRON_MOCK:
        with get_or_create_app(__name__, ROUTES).test_client() as c:
            data = {
                'title': BaseTestFactory.create_random_string(),
                'body': BaseTestFactory.create_random_string(),
                'date': date.today(),
                'date-time': datetime.utcnow()
            }
            result = c.post(
                '/messages', data=json.dumps(data),
                content_type='application/json'
            )
            assert 400 == result.status_code
            j_content = json.loads(result.get_data().decode('utf-8'))
            assert "is not a 'date'" in j_content['msg']

            serializer = NewMessage(data=data)
            result = c.post(
                '/messages', data=serializer.payload,
                content_type='application/json'
            )
            assert 201 == result.status_code


def test_http_put():
    with OS_ENVIRON_MOCK:
        with get_or_create_app(__name__, ROUTES).test_client() as c:
            data = {
                'key': uuid.uuid4(),
                'title': BaseTestFactory.create_random_string(),
                'body': BaseTestFactory.create_random_string(),
                'date': date.today(),
                'date-time': datetime.utcnow()
            }
            serializer = Message(data=data)
            result = c.put(
                '/messages/{}'.format(data['key']),
                data=serializer.payload,
                content_type='application/json'
            )
            assert 404 == result.status_code

            data['key'] = 'f3f99fe6-3099-4fc4-aad4-31babad961c6'
            serializer = Message(data=data)
            result = c.put(
                '/messages/{}'.format(data['key']),
                data=serializer.payload,
                content_type='application/json'
            )
            assert 200 == result.status_code


def test_http_post_sql():
    with OS_ENVIRON_MOCK:
        app = get_or_create_app(__name__, ROUTES)
        with app.app_context():
            pool = create_pool()
            syncdb(pool=pool)
            cleandb(pool=pool)
            assert 0 == BookModel.objects.count()

            with app.test_client() as c:

                data = {
                    'title': BaseTestFactory.create_random_string(),
                }

                serializer = BookSerializer(data=data)
                result = c.post(
                    '/books', data=serializer.payload,
                    content_type='application/json'
                )
                assert 201 == result.status_code
                assert 1 == BookModel.objects.count()
