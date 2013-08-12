from test.base import ApiBaseTestCase, raises, ModelTestFactory
from users.models import User, AuthenticationError

from sqlalchemy.exc import IntegrityError


class UserModelTestCase(ApiBaseTestCase):
    @raises(IntegrityError)
    def test_fail_create_required_fields(self):
        user = User()
        user.add()

    @raises(AuthenticationError)
    def test_fail_invalid_access_token(self):
        user = ModelTestFactory.get_user()
        User.authenticate(user.username, '123')

    def test_authentication_ok(self):
        user = ModelTestFactory.get_user()
        user2 = User.authenticate(user.username, user.access_token)
        self.assertEquals(user.id, user2.id)
