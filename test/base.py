from users.models import User

import random
import string
import unittest


class ApiBaseTestCase(unittest.TestCase):
    def _init_db(self):
        from sqlalchemy.ext.declarative import declarative_base
        from common.models import get_engine
        from users.models import User
        engine = get_engine()
        Base = declarative_base()
        User.metadata.create_all(engine)

    def setUp(self):
        import users.views
        self.client = users.views.app.test_client()
        self._init_db()

    def tearDown(self):
        import os
        try:
            os.remove('test.db')
        except OSError:
            pass


class raises(object):
    """ Decorator class that chekcks if a particular exception has raised in unit testing
        see: http://stackoverflow.com/questions/2692402/unittest-in-django-how-to-get-the-exception-message-from-assertraises
        http://www.artima.com/weblogs/viewpost.jsp?thread=240808
    """
    def __init__(self, exception):
        self.exception = exception

    def __call__(self, f):
        def wrapped_f(*args):
            try:
                f(*args)
            except self.exception, e:
                pass
            except:
                raise
            else:
                msg = "{0}() did not raise {1}".format(f.__name__, self.exception.__name__)
                raise AssertionError(msg)
        return wrapped_f



class ModelTestFactory(object):
    """
    Factory class that create models by demand on unit tests
    """
    @classmethod
    def create_unique_string(cls, prefix='', n_range=6):
        st = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(n_range))
        if prefix:
            return '{0}-{1}'.format(prefix, st)
        else:
            return '{0}'.format(st)

    @classmethod
    def create_unique_email(cls):
        return '{0}@{1}.com'.format(ModelTestFactory.create_unique_string(),
                                    ModelTestFactory.create_unique_string())

    @classmethod
    def get_user(cls, **kwargs):
        if 'email' not in kwargs:
            kwargs['email'] = ModelTestFactory.create_unique_email()

        if 'username' not in kwargs:
            kwargs['username'] = ModelTestFactory.create_unique_string()

        if 'first_name' not in kwargs:
            kwargs['first_name'] = ModelTestFactory.create_unique_string()

        if 'last_name' not in kwargs:
            kwargs['last_name'] = ModelTestFactory.create_unique_string()

        obj = User(**kwargs)
        obj.add()
        return obj
