from sqlalchemy import Text
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID

import uuid
import bcrypt


class PasswordHash(object):
    """
    http://variable-scope.com/posts/storing-and-verifying-passwords-with-sqlalchemy
    """
    def __init__(self, hash_):
        assert len(hash_) == 60, 'bcrypt hash should be 60 chars.'

        if isinstance(hash_, bytes):
            self.hash = hash_.decode('utf-8')
        else:
            self.hash = hash_

        assert self.hash.count('$'), 'bcrypt hash should have 3x "$".'
        self.rounds = int(self.hash.split('$')[2])

    def __eq__(self, candidate):
        """Hashes the candidate string and compares it to the stored hash."""
        if isinstance(self.hash, str):
            _hash = self.hash.encode('utf-8')
        else:
            _hash = self.hash

        if isinstance(candidate, PasswordHash):
            candidate = candidate.hash

        if isinstance(candidate, str):
            candidate = candidate.encode('utf-8')

        return bcrypt.hashpw(candidate, _hash) == _hash

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        """Simple object representation."""
        return '<{}>'.format(type(self).__name__)

    @classmethod
    def new(cls, password, rounds):
        """Creates a PasswordHash from the given password."""
        if isinstance(password, str):
            password = password.encode('utf8')
        value = bcrypt.hashpw(password, bcrypt.gensalt(rounds))
        return cls(value)


class Password(TypeDecorator):
    """Allows storing and retrieving password hashes using PasswordHash."""
    impl = Text

    def __init__(self, rounds=12, **kwds):
        self.rounds = rounds
        super(Password, self).__init__(**kwds)

    def process_bind_param(self, value, dialect):
        """Ensure the value is a PasswordHash and then return its hash."""
        return self._convert(value).hash

    def process_result_value(self, value, dialect):
        """Convert the hash to a PasswordHash, if it's non-NULL."""
        if value is not None:
            return PasswordHash(value)

    def validator(self, password):
        """Provides a validator/converter for @validates usage."""
        return self._convert(password)

    def _convert(self, value):
        """Returns a PasswordHash from the given string.

        PasswordHash instances or None values will return unchanged.
        Strings will be hashed and the resulting PasswordHash returned.
        Any other input will result in a TypeError.
        """
        if isinstance(value, PasswordHash):
            return value
        elif isinstance(value, str):
            value = value.encode('utf-8')
            return PasswordHash.new(value, self.rounds)
        elif value is not None:
            raise TypeError(
                'Cannot convert {} to a PasswordHash'.format(type(value)))


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses Postgresql's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    .. seealso::

        http://docs.sqlalchemy.org/en/latest/core/types.html#backend-agnostic-guid-type

    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value)
            else:
                # hexstring
                return "%.32x" % value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)
