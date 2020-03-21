from serializers import JsonSerializer
from jsonschema.exceptions import ValidationError


class SignUpSerializer(JsonSerializer):
    _schema = {
        'type': 'object',
        'properties': {
            'email': {'type': 'string', 'format': 'email'},
            'password1': {'type': 'string'},
            'password2': {'type': 'string'},
        },
        'required': ['email', 'password1', 'password2']
    }

    def validate(self):
        super(SignUpSerializer, self).validate()
        if self._data['password1'] != self._data['password2']:
            raise ValidationError('Passwords must be equal')
