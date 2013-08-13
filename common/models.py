from common.serializer import JsonSerializer

from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker, scoped_session

import sys


if 'test' in sys.argv:
    conection_string = 'sqlite:///test.db'
else:
    conection_string = 'sqlite:///music.db'


def get_engine(*args, **kwargs):
    return create_engine(conection_string)


class SessionFactory(object):
    """Db session must be shared between objects, for this reason this class
       implements singleton and Factory method in order to crate unique db session between
       objects
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SessionFactory, cls).__new__(cls, *args, **kwargs)
            engine = get_engine()
            sm = sessionmaker(bind=engine)
            cls._instance.session = scoped_session(sm)

        return cls._instance

    def get_session(self):
        return self.session


def get_session(*args, **kwargs):
    factory = SessionFactory()
    return factory.get_session()


def close_session():
    session = get_session()
    session.close_all()


class BaseManager(object):
    """
    Base manager, every model will have this common manager that allows permorf database common operations
    """
    def __init__(self, model, *args, **kwargs):
        self._model = model
        self.session = get_session()

    def filter_by(self, order_by='id', limit=500, offset=0, **kwargs):
        return self.session.query(self._model).filter_by(**kwargs).order_by(order_by).limit(limit).offset(offset)

    def get(self, id):
        return self.session.query(self._model).get(id)


Base = declarative_base()


class BaseModel(Base, JsonSerializer):
    """Abstract base model, contiains common field and methods for all models
    """
    __abstract__ = True

    def __init__(self, *args, **kwargs):
        self.session = get_session()
        for name, value in kwargs.items():
            setattr(self, name, value)

    def close_session(self):
        if self.session:
            self.session.close_all()

    id = Column(Integer, primary_key=True)

    @declared_attr
    def objects(cls):
        return BaseManager(cls)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @classmethod
    def raw_sql(cls, sql, **kwargs):
        if not hasattr(cls, 'session'):
            cls.session = get_session()
        return cls.session.execute(sql, kwargs)

    def update(self):
        try:
            if not hasattr(self, 'session'):
                self.session = get_session()
            self.session.commit()
        except Exception as error:
            self.session.rollback()
            raise error

    def add(self):
        try:

            if not hasattr(self, 'session'):
                self.session = get_session()

            self.session.add(self)
            self.session.commit()
        except Exception as error:
            self.session.rollback()
            raise error

    def delete(self):
        try:
            if not hasattr(self, 'session'):
                self.session = get_session()

            self.session.delete(self)
            self.session.commit()
        except Exception as error:
            self.session.rollback()
            raise error
