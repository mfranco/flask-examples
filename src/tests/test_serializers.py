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
