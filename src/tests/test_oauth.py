from oauth import (
    OAuth2User, OAuth2Client, OAuth2AuthorizationCode, OAuth2Token)


mock_env = {
    'FLASK_CONFIG_PREFIXES': 'SQLALCHEMY',
    'SQLALCHEMY_DEFAULT': 'postgresql://ds:dsps@pgdb:5432/ds_test',
}


def test_oauth():
    with os_environ_mock:
        app = get_or_create_app(__name__)
        with app.app_context():

            pool = create_pool()
            syncdb(pool=pool)
            cleandb(pool=pool)
