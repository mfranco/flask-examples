from datetime import date, datetime
from decimal import Decimal
from flask import json
from jsonschema import validate, FormatChecker
from jsonschema.exceptions import ValidationError

import typing
import uuid


class SerializerError(Exception):
    """
    This exception should be thrown if serializer errors happen
    """


class JsonSerializer(object):
    """
    Base serializer
    """
    _schema: typing.Dict = {}

    _data: typing.Dict = {}

    _payload: str = None

    _data_to_validate: typing.Dict = {}

    _properties: typing.Dict = {}

    def __init__(self, payload: str = None, data: typing.Dict = None):
        """
        A serializer object can be built from a dictionary or
        a json serialized string
        """

        if data:
            self.initialize(data)

        elif payload:
            self._payload = payload
            data = json.loads(self._payload, parse_float=Decimal)
            self.initialize(data)
        else:
            raise SerializerError(
                'Can not build a serializer without'
                'a data dictionary or string payload associated')

    def custom_converter(
            self, o: typing.Union[uuid.UUID, date, datetime]) -> str:
        if type(o) == uuid.UUID:
            return str(o)
        elif type(o) == date:
            return o.isoformat()
        elif type(o) == datetime:
            return o.astimezone().isoformat()

    def validate(self) -> None:
        # avoid extra values not defined in the schema
        if 'additionalProperties' not in self._schema:
            self._schema['additionalProperties'] = True

        try:
            validate(
                self._data_to_validate, self._schema,
                format_checker=FormatChecker())
        except ValidationError as e:
            instances = (
                uuid.UUID, date, datetime
            )
            if type(e.instance) in instances:
                # jsonchema can not deal with uuid validation
                # so string conversion is a way to handle this
                self._data_to_validate = json.loads(
                    self.dumps(), parse_float=Decimal)
            validate(
                self._data_to_validate, self._schema,
                format_checker=FormatChecker())
        finally:
            self._data_to_validate = None

    def initialize(self, data: typing.Dict) -> None:
        """
        Loads serializer from a request object
        """
        self._data = data
        self._data_to_validate = self._data.copy()
        self.validate()

    @property
    def data(self) -> typing.Dict:
        """
        Returns a json representation
        """
        return self._data

    @property
    def payload(self) -> str:
        return self.dumps()

    def dumps(self, indent: int = 4):
        return json.dumps(
            self._data, default=self.custom_converter, indent=indent)
