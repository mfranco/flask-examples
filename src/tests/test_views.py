from flask import json, request, Response, current_app
from app import get_or_create_app
from serializers import JsonSerializer, SerializerError
from views import json_response, BaseResourceView
from tests.base import BaseTestFactory

from datetime import date, datetime
from jsonschema.exceptions import ValidationError
from unittest.mock import Mock, patch

import os
import sys
import typing
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


# class based view
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


# simple function view
@flask_bh_decorator
def message_post() -> Response:
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


# Mocking routes module
routes_mock = Mock()

routes_mock.ROUTES = (
    {
        'rule': '/messages', 'endpoint': 'messages',
        'view_func': MessageView.as_view('messages')
    },
    {
        'rule': '/messages/<uuid:key>', 'endpoint': 'home_key',
        'view_func': MessageView.as_view('messages_key')
    },
    {
        'rule': '/messages-func', 'endpoint': 'messages_func',
        'view_func': message_post, 'methods': ['POST']
    },
)

sys_modules_mock = {
    'routes': routes_mock
}

mock_env = {
    'FLASK_BH_LOG_LEVEL': 'DEBUG'
}

os_environ_mock = patch.dict(os.environ, mock_env)


def test_http_get():
    with patch.dict(sys.modules, sys_modules_mock), os_environ_mock:
        initialize_flask_bh(__name__)
        view = MessageView()
        result = view.get()
        assert 200 == result.status_code
        j_content = json.loads(result.get_data().decode('utf-8'))
        assert 2 == len(j_content)


def test_http_post_method_view():
    with patch.dict(sys.modules, sys_modules_mock), os_environ_mock:
        with initialize_flask_bh(__name__).test_client() as c:
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


def test_http_post_function_view():
    with patch.dict(sys.modules, sys_modules_mock), os_environ_mock:
        with initialize_flask_bh(__name__).test_client() as c:
            data = {
                'title': BaseTestFactory.create_random_string(),
                'body': BaseTestFactory.create_random_string(),
                'date': date.today(),
                'date-time': datetime.utcnow()
            }
            serializer = NewMessage(data=data)
            result = c.post(
                '/messages-func', data=serializer.payload,
                content_type='application/json'
            )
            assert 201 == result.status_code


def test_http_put():
    with patch.dict(sys.modules, sys_modules_mock), os_environ_mock:
        with initialize_flask_bh(__name__).test_client() as c:
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


@flask_bh_decorator
def aws_create_message(event: typing.Dict, context: typing.Any) -> typing.Dict:
    app = current_app._get_current_object()
    try:
        serializer = NewMessage(data=event['body'])
        data = serializer.data
        data['key'] = uuid.uuid4()
        new_data = Message(data=data)
        return {
            'statusCode': 201,
            'body': new_data.payload
        }

    except ValidationError as e:
        data = {
            'code': 400,
            'message': e.message
        }
        serializer = Error(data=data)
        return {
            'statusCode': 400,
            'body': serializer.payload
        }

    except Exception as e:
        app.logger.error(e)
        data = {
            'code': 500,
            'message': 'Internal error'
        }
        serializer = Error(data=data)
        return {
            'statusCode': 500,
            'body': serializer.payload
        }


def test_aws_lambda_view():

    data = {
        'title': BaseTestFactory.create_random_string(),
        'body': BaseTestFactory.create_random_string(),
        'date': date.today(),
        'date-time': datetime.utcnow()
    }
    serializer = NewMessage(data=data)

    event = {
        'body': serializer.data,
        'method': 'POST',
        'pathParameters': {
        },
        'queryStringParameters': None
    }
    context = Mock()
    with os_environ_mock:
        result = aws_create_message(event, context)
        serializer2 = Message(payload=result['body'])
        for k in data.keys():
            assert k in serializer2.data
