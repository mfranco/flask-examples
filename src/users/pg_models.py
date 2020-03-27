from pg.orm import BaseModel
from pg.types import Password

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID


class User(BaseModel):
    __tablename__ = 'users'
    key = Column(UUID(as_uuid=True), unique=True)
    username = Column(String(64), unique=True)
    password = Column(Password)

    def get_user_id(self):
        return self.key

    @classmethod
    def check_password(cls, username=None, password=None):
        user = cls.objects.get(username=username)
        assert user.password == password
        return user
