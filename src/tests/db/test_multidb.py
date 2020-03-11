from models.orm import BaseModel, syncdb, cleandb
from models.orm.connection import create_pool
from sqlalchemy import Column, String
from app import get_or_create_app
from unittest.mock import patch

import os


class Example(BaseModel):
    __tablename__ = 'example'
    name = Column(String(256))


def test_muti_crud():
    mock_env = {
        'FLASK_CONFIG_PREFIXES': 'SQLALCHEMY',
        'SQLALCHEMY_DEFAULT': 'postgresql://ds:dsps@pgdb:5432/ds_test',
        'SQLALCHEMY_DB2': 'postgresql://ds:dsps@pgdb:5432/ds2_test'
    }

    os_environ_mock = patch.dict(os.environ, mock_env)

    with os_environ_mock:
        app = get_or_create_app(__name__)

        with app.app_context():
            pool = create_pool()
            syncdb(pool=pool)
            cleandb(pool=pool)

            rock = Example(name='Rock')
            rock.add(connection_name='SQLALCHEMY_DEFAULT')
            pool.commit(connection_name='SQLALCHEMY_DEFAULT')

            assert 1 == Example.objects.count(
                connection_name='SQLALCHEMY_DEFAULT')
            assert 0 == Example.objects.count(
                connection_name='SQLALCHEMY_DB2')

            rock2 = Example(name='Rock2')
            rock2.add(connection_name='SQLALCHEMY_DB2')
            pool.commit(connection_name='SQLALCHEMY_DB2')

            assert 1 == Example.objects.count(
                connection_name='SQLALCHEMY_DB2')

            r1 = Example.objects.get(
                connection_name='SQLALCHEMY_DEFAULT', name='Rock')
            r2 = Example.objects.get(
                connection_name='SQLALCHEMY_DB2', name='Rock2')

            assert r1.name != r2.name

            rock.delete()
            pool.commit()
            assert 0 == Example.objects.count(
                connection_name='SQLALCHEMY_DEFAULT')

            l1 = list(
                Example.objects.filter_by(
                    connection_name='SQLALCHEMY_DEFAULT'))
            l2 = list(
                Example.objects.filter_by(connection_name='SQLALCHEMY_DB2'))

            assert 0 == len(l1)
            assert 1 == len(l2)
            cleandb(pool=pool)
