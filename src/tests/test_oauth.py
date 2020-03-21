from oauth.models import (
    OAuth2User, OAuth2Client, OAuth2AuthorizationCode, OAuth2Token)
from oauth import config_oauth
from unittest.mock import patch
from app import get_or_create_app
from oauth.views import signup
from pg import PGSqlAlchemy
import os


mock_env = {
    'FLASK_CONFIG_PREFIXES': 'SQLALCHEMY',
    'SQLALCHEMY_DEFAULT': 'postgresql://ds:dsps@pgdb:5432/ds_test',
}


os_environ_mock = patch.dict(os.environ, mock_env)

def config_app(app):
    db = PGSqlAlchemy(app)
    db.syncdb()
    db.cleandb()
    config_oauth(app)



def test_oauth():
    with os_environ_mock:
        app = get_or_create_app(__name__)
        with app.app_context():
            config_app(app)
            
