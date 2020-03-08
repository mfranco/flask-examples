from flask import current_app, _app_ctx_stack
from flask_philo_core import ConfigurationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session


class Connection(object):
    def __init__(self, engine, session):
        """
        Encapsulates  an engine and session to a database
        """
        self.engine = engine
        self.session = session


class ConnectionPool:
    """
    Flask-philo supports multiple postgresql database connections,
    this class stores one connection by every db
    """
    connections = {}

    def __init__(self, app=None):
        self.app = app

    def initialize_connections(self, scopefunc=None):
        """
        Initialize a database connection by each connection string
        defined in the configuration file
        """
        for connection_name, connection_string in\
                self.app.config['FLASK_PHILO_SQLALCHEMY'].items():
            engine = create_engine(connection_string)
            session = scoped_session(sessionmaker(), scopefunc=scopefunc)
            session.configure(bind=engine)
            self.connections[connection_name] = Connection(engine, session)

    def close(self):
        for k, v in self.connections.items():
            v.session.remove()

    def commit(self, connection_name='DEFAULT'):
        if connection_name is None:
            for conn_name, conn in self.connections.items():
                conn.session.commit()
        else:
            self.connections[connection_name].session.commit()

    def rollback(self, connection_name='DEFAULT'):
        if connection_name is None:
            for conn_name, conn in self.connections.items():
                conn.session.rollback()
        else:
            self.connections[connection_name].session.rollback()


def create_pool():
    app = current_app._get_current_object()
    if 'FLASK_PHILO_SQLALCHEMY' not in app.config:
        raise ConfigurationError(
            'Not configuration found for Flask_Philo_SQLAlchemy')
    ctx = _app_ctx_stack.top
    if ctx is not None:
        if not hasattr(ctx, 'sqlalchemy_pool'):
            pool = ConnectionPool(app)
            pool.initialize_connections(scopefunc=_app_ctx_stack)
            ctx.sqlalchemy_pool = pool
        else:
            pool = ctx.sqlalchemy_pool

        @app.before_request
        def before_request():
            """
            Assign postgresql connection pool to the global
            flask object at the beginning of every request
            """
            ctx = _app_ctx_stack.top
            pool = ConnectionPool(app)
            pool.initialize_connections(scopefunc=_app_ctx_stack)
            ctx.sqlalchemy_pool = pool

        @app.teardown_request
        def teardown_request(exception):
            """
            Releasing connection after finish request, not required in unit
            testing
            """
            ctx = _app_ctx_stack.top
            pool = getattr(ctx, 'sqlalchemy_pool', None)
            if pool is not None:
                for k, v in pool.connections.items():
                    v.session.remove()
        return pool
