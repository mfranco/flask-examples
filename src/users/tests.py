from .pg_models import User
from oauth.pg_models import OAuth2User
from .serializers import SignUpSerializer
from users import config_users
from unittest.mock import patch
from app import get_or_create_app
from pg import init_db
from tests.base import BaseTestFactory

import os
from flask import json
import uuid


mock_env = {
    'FLASK_CONFIG_PREFIXES': 'SQLALCHEMY',
    'SQLALCHEMY_DEFAULT': 'postgresql://ds:dsps@pgdb:5432/ds_test',
}


os_environ_mock = patch.dict(os.environ, mock_env)

def config_app(app):
    db = init_db(app)

    db.syncdb()
    db.cleandb()
    config_users(app)

def create_user():
    pwd = BaseTestFactory.create_random_string()
    data = {
        'username': BaseTestFactory.create_random_email(),
        'password': pwd,
        'password2': pwd,
        'key': uuid.uuid4()
    }
    user = User(**data)
    user.add()
    user.objects.db.pool.commit()
    return user, pwd



def test_signup_username_password():
    with os_environ_mock:
        app = get_or_create_app(__name__)
        with app.app_context():
            config_app(app)

            with app.test_client() as c:
                p1 = BaseTestFactory.create_random_string()
                p2 = BaseTestFactory.create_random_string()
                assert p1 != p2
                data = {
                    'username': BaseTestFactory.create_random_email(),
                    'password': p1,
                    'password2': p2,
                }

                result = c.post(
                    '/users/signup', data=json.dumps(data),
                    content_type='application/json'
                )
                assert 400 == result.status_code
                j_content = json.loads(result.get_data().decode('utf-8'))
                assert "Passwords must be equal" in j_content['msg']
                assert 0 == User.objects.count()
                assert 0 == OAuth2User.objects.count()

                pwd = BaseTestFactory.create_random_string()
                data2 = {
                    'username': BaseTestFactory.create_random_email(),
                    'password': pwd,
                    'password2': pwd,
                }
                serializer = SignUpSerializer(data=data2)

                result = c.post(
                    '/users/signup', data=serializer.payload,
                    content_type='application/json'
                )
                assert 201 == result.status_code
                assert 1 == User.objects.count()
                assert 1 == OAuth2User.objects.count()
