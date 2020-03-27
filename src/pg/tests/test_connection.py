from pg import init_db
from app import get_or_create_app
from unittest.mock import patch

import os

def test_postgresql_connection():
    """
    checks if connection is open
    """

    mock_env = {
        'FLASK_CONFIG_PREFIXES': 'SQLALCHEMY',
        'SQLALCHEMY_DEFAULT': 'postgresql://ds:dsps@pgdb:5432/ds_test',
    }

    os_environ_mock = patch.dict(os.environ, mock_env)

    with os_environ_mock:
        app = get_or_create_app(__name__)
        with app.app_context():
            db = init_db(app)
            result = db.pool.connections['SQLALCHEMY_DEFAULT'].session.execute(
                'SELECT 19;')
            assert result.fetchone()[0] == 19
            db.pool.connections['SQLALCHEMY_DEFAULT'].session.close()
