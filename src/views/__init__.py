from flask import json, Response, current_app, _app_ctx_stack
from models.orm.connection import create_pool
from flask.views import MethodView

import typing


def json_response(
        status: int = 200, data: typing.Dict = {},
        headers: typing.Dict = {}) -> Response:
    mimetype:str = 'application/json'
    return Response(
        json.dumps(data), status=status, mimetype=mimetype, headers=headers)



class BaseResourceView(MethodView):

    def get(self, *args, **kwargs) -> Response:
        return json_response(status=400)

    def post(self, *args, **kwargs) -> Response:
        return json_response(status=400)

    def put(self, *args, **kwargs) -> Response:
        return json_response(status=400)

    def patch(self, *args, **kwargs) -> Response:
        return json_response(status=400)

    def delete(self, *args, **kwargs) -> Response:
        return json_response(status=400)



class SQLAlchemyView(BaseResourceView):
    def __init__(self):
        self.app = current_app._get_current_object()
        if 'FLASK_SQLALCHEMY' not in self.app.config:
            raise ConfigurationError(
                'Not configuration found for Flask_SQLAlchemy')
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'sqlalchemy_pool'):
                ctx.sqlalchemy_pool = create_pool()
        self.sqlalchemy_pool = ctx.sqlalchemy_pool
