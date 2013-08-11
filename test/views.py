from users.views import *
from test.common import ApiBaseTestCase

class UserViewsTestCase(ApiBaseTestCase):
    def test_get_user_request(self):
        response = self.client.get('/users/')
        print(response.data)

    def test_fail_create_required_fields(self):
        print("7")
        pass

    def test_fail_username_unique(self):
        print("8")
        pass

    def test_fail_invalid_access_token(self):
        print("9")
        pass
