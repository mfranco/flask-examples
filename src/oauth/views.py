from flask import request, json, Response, current_app
from oauth.serializers import SignUpSerializer
from jsonschema.exceptions import ValidationError
from utils import json_response
from oauth.models import OAuth2User

import uuid


def signup() -> Response:
    app = current_app._get_current_object()
    try:
        serializer = SignUpSerializer(data=request.json)
        data = serializer.data
        del data['password2']
        data['key'] = uuid.uuid4()
        obj = OAuth2User(**data)
        obj.add()
        obj.objects.db.pool.commit()
        return json_response(status=201, data={'key': data['key']})

    except ValidationError as e:
        return json_response(status=400, data={'msg': e.message})

    except Exception as e:
        app.logger.error(e)
        return json_response(status=500)
