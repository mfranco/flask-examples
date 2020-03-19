from pg.connection import ConnectionPool
from flask import _app_ctx_stack

class PGSqlAlchemy(object):
    def __init__(self, app):
        self.app = app

        if 'SQLALCHEMY_DEFAULT' not in self.app.config:
            raise Exception(
                'Not configuration found for SQLAlchemy')

        ctx = _app_ctx_stack.top

        if ctx is not None:
            if not hasattr(ctx, 'sqlalchemy_pool'):
                pool = ConnectionPool(scopefunc=_app_ctx_stack)
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
                pool = ConnectionPool(scopefunc=_app_ctx_stack)
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
        self.pool = pool

    def syncdb(self):
        from pg.orm import BaseModel
        """
        Create tables if they don't exist
        """
        for conn_name, conn in self.pool.connections.items():
            BaseModel.metadata.create_all(conn.engine)


    def cleandb(self):
        from pg.orm import BaseModel
        for t in reversed(BaseModel.metadata.sorted_tables):
            sql = 'delete from {} cascade;'.format(t.name)
            for conn_name, conn in self.pool.connections.items():
                conn.session.execute(sql)
                conn.session.commit()
