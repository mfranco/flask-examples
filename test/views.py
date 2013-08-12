from users.models import User
from users.views import *
from test.base import ApiBaseTestCase

class UserViewsTestCase(ApiBaseTestCase):
    def test_get_user_request(self):
        response = self.client.get('/users/')
        self.assertRegexpMatches(response.data, '.*ENDPOINT')

    def test_fail_create_required_fields(self):
        self.assertEquals(0, User.objects.filter_by().count())
        print("7")
        pass

    def test_fail_username_unique(self):
        print("8")
        pass

    def test_fail_invalid_access_token(self):
        print("9")
        pass
