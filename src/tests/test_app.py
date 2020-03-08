from flask import current_app
from app import get_or_create_app
from unittest.mock import patch

import os
import pytest


def test_app_creation():
    """
    Test if flask_bh app is created
    properly
    """
    # Raises an exception for uninitialized apps
    with pytest.raises(RuntimeError):
        current_app._get_current_object()

    app = get_or_create_app(__name__)

    with app.app_context():
        """
        verifies that current_app._get_current_object()
        returns same object previusly created

        see: with app.app_context():
        """
        app2 = current_app._get_current_object()
        assert app == app2
        assert app.name == __name__


def test_app_config():
    """
    Test if app loads configuration values from
    environmnet variables properly
    """
    mock_env = {
        'FLASK_CONFIG_PREFIXES': 'AWS,DB',
        'AWS_SECRET': 'S3CR3T',
        'DB_USERNAME': 'USER',
        'PREFIX_NOT_EXISTS': 'SHOULD_NOT_EXIST',
        'FLASK_BH_DEBUG_LEVEL': 'DEBUG'
    }

    os_environ_mock = patch.dict(os.environ, mock_env)

    with os_environ_mock:
        app = get_or_create_app(__name__)
        assert 'AWS_SECRET' in app.config
        assert 'DB_USERNAME' in app.config
        assert 'PREFIX_NOT_EXISTS' not in app.config
