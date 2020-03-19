from flask import current_app
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
    Multiple postgresql database connections support
    """
    connections = {}

    def __init__(self, scopefunc=None):
        self.scopefunc = scopefunc
        self.app = current_app._get_current_object()
        self.initialize_connections()

    def initialize_connections(self):
        """
        Initialize a database connection by each connection string
        defined in the configuration file
        """

        for k, v in self.app.config.items():
            if k.startswith('SQLALCHEMY'):
                connection_string = v
                connection_name = k
                engine = create_engine(connection_string)
                session = scoped_session(sessionmaker(), scopefunc=self.scopefunc)
                session.configure(bind=engine)
                self.connections[connection_name] = Connection(engine, session)


    def get_session(self, connection_name='SQLALCHEMY_DEFAULT'):
        return self.connections[connection_name].session


    def close(self):
        for k, v in self.connections.items():
            v.session.remove()

    def commit(self, connection_name='SQLALCHEMY_DEFAULT'):
        if connection_name is None:
            for conn_name, conn in self.connections.items():
                conn.session.commit()
        else:
            self.connections[connection_name].session.commit()

    def rollback(self, connection_name='SQLALCHEMY_DEFAULT'):
        if connection_name is None:
            for conn_name, conn in self.connections.items():
                conn.session.rollback()
        else:
            self.connections[connection_name].session.rollback()



