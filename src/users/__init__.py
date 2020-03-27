from .blueprint import users_bp


def config_users(app):
    app.register_blueprint(users_bp, url_prefix='/users')
