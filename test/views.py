from users.models import User
from users.views import *
from test.base import ApiBaseTestCase

import json


class UserViewsTestCase(ApiBaseTestCase):
    def test_get_user_request(self):
        response = self.client.get('/users/')
        self.assertRegexpMatches(response.data, '.*ENDPOINT')

    def test_fail_create_required_fields(self):
        self.assertEquals(0, User.objects.filter_by().count())

    def test_create_user(self):
        self.assertEquals(0, User.objects.filter_by().count())
        data = {'username': 'maigfrga', 'email': 'maigfrga@gmail.com',
                'first_name': 'Manuel', 'last_name': 'Franco'}
        url = '/users/'
        response = self.json_request(url, data)
        self.assertEquals(1, User.objects.filter_by().count())
        json_dict_response = json.loads(response.data)
        self.assertEquals(data['username'], json_dict_response['user']['username'])

    def test_fail_username_unique(self):
        pass

    def test_fail_invalid_access_token(self):
        pass

