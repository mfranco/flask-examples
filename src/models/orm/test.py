from flask_philo_core.test import FlaskPhiloTestCase
from flask_philo_sqlalchemy.connection import create_pool
from flask_philo_sqlalchemy import cleandb, syncdb


class SQLAlchemyTestCase(FlaskPhiloTestCase):
    def setup(self):
        super(SQLAlchemyTestCase, self).setup()
        with self.app.app_context():
            self.pool = create_pool()
            syncdb(pool=self.pool)

    def teardown(self):
        with self.app.app_context():
            cleandb()
            self.pool.close()
