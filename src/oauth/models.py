from pg.orm import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String, Numeric, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from pg.types import Password

from authlib.integrations.sqla_oauth2 import (
    OAuth2ClientMixin,
    OAuth2AuthorizationCodeMixin,
    OAuth2TokenMixin,
)


class OAuth2User(BaseModel):
    __tablename__ = 'oauth2_users'
    key = Column(UUID(as_uuid=True))
    username = Column(String(64), unique=True)
    password = Column(Password)

    def get_user_id(self):
        return self.key

    @classmethod
    def authenticate(cls, username=None, password=None):
        user = OAuth2User.objects.get(username=username)
        assert user.password == password


class OAuth2Client(BaseModel, OAuth2ClientMixin):
    __tablename__ = 'oauth2_client'

    user_ = Column(
        UUID, ForeignKey('oauth2_users.key', ondelete='CASCADE'))
    user = relationship('OAuth2User')


class OAuth2AuthorizationCode(BaseModel, OAuth2AuthorizationCodeMixin):
    __tablename__ = 'oauth2_code'

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey('oauth2_users.id', ondelete='CASCADE'))
    user = relationship('OAuth2User')


class OAuth2Token(BaseModel, OAuth2TokenMixin):
    __tablename__ = 'oauth2_token'

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey('oauth2_users.id', ondelete='CASCADE'))
    user = relationship('OAuth2User')

    def is_refresh_token_active(self):
        if self.revoked:
            return False
        expires_at = self.issued_at + self.expires_in * 2
        return expires_at >= time.time()
