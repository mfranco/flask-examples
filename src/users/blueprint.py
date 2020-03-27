from flask import Blueprint
from flask import request, json, Response, current_app
from flask import _app_ctx_stack
from jsonschema.exceptions import ValidationError
from utils import json_response
from .pg_models import User
from .serializers import SignUpSerializer
from oauth import create_user as create_oauth_user

import uuid


users_bp = Blueprint('users', __name__)



@users_bp.route('/signup', methods=['POST'])
def signup() -> Response:
    app = current_app._get_current_object()
    ctx = _app_ctx_stack.top
    db = ctx.pg_sqlalchemy
    try:
        serializer = SignUpSerializer(data=request.json)
        data = serializer.data
        del data['password2']
        data['key'] = str(uuid.uuid4())
        obj = User(**data)
        obj.add()
        db.pool.commit()
        create_oauth_user(key=data['key'], username=data['username'])
        return json_response(status=201, data={'key': data['key']})

    except ValidationError as e:
        db.pool.rollback()
        return json_response(status=400, data={'msg': e.message})

    except Exception as e:
        db.pool.rollback()
        app.logger.error(e)
        return json_response(status=500)
