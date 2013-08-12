from common.models import BaseModel

from sqlalchemy import Column, String


class AuthenticationError(Exception):
    pass

class User(BaseModel):
    username = Column(String(256), index=True, unique=True, nullable=False)
    email = Column(String(256), index=True, unique=True, nullable=False)
    access_token = Column(String(256), nullable=False)
    first_name = Column(String(256), nullable=False)
    last_name = Column(String(256), nullable=False)

    @classmethod
    def authenticate(cls, username, access_token):
        """Check if an access_token by username is valid
        """
        try:
             return User.objects.filter_by(username=username, access_token=access_token)[0]
        except Exception as error:
            raise AuthenticationError('invalid credentials')

    def add(self):
        self.access_token = self.generate_access_token()
        super(User, self).add()

    def generate_access_token(self):
        """Very simple access token generation, should be re written before put in production
        """
        import os
        return os.urandom(16).encode('hex')

    def __repr__(self):
        return '<User> {0}-{1}'.format(self.username, self.email)
