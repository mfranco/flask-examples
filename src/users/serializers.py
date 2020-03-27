from serializers import JsonSerializer
from jsonschema.exceptions import ValidationError


class SignUpSerializer(JsonSerializer):
    _schema = {
        'type': 'object',
        'properties': {
            'username': {'type': 'string'},
            'password': {'type': 'string'},
            'password2': {'type': 'string'},
        },
        'required': ['username', 'password', 'password2']
    }

    def validate(self):
        super(SignUpSerializer, self).validate()
        if self._data['password'] != self._data['password2']:
            raise ValidationError('Passwords must be equal')
