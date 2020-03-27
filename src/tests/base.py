from decimal import Decimal

import random
import string
import uuid


class BaseTestFactory(object):
    @classmethod
    def create_random_uuid(cls) -> uuid.UUID:
        return uuid.uuid4()

    @classmethod
    def create_random_string(
            cls, prefix: str = None, n_range: int = 20) -> str:
        st = ''.join(
            random.choice(
                string.ascii_lowercase + string.digits)
            for x in range(n_range))

        if prefix:
            return '{0}{1}'.format(prefix, st)
        else:
            return '{0}'.format(st)

    @classmethod
    def create_random_email(cls, prefix: str = None) -> str:
        return '{0}@{1}.com'.format(
            cls.create_random_string(), cls.create_random_string())

    @classmethod
    def create_random_decimal(cls, n=10000):
        return Decimal((random.randrange(n)/100))
