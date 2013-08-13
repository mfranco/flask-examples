from users.models import User
from users.views import *
from test.base import ApiBaseTestCase, ModelTestFactory

import json


class UserViewsTestCase(ApiBaseTestCase):
    def setUp(self):
        super(UserViewsTestCase, self).setUp()
        self.users_url = '/users/'

    def test_get_user_request_info(self):
        user = ModelTestFactory.get_user()
        response = self.json_request_with_credentials(self.users_url, method='get',
                                                      username=user.username,
                                                      access_token=user.access_token)
        json_dict_response = json.loads(response.data)
        self.assertEquals(user.username, json_dict_response['username'])

    def test_fail_create_required_fields(self):
        self.assertEquals(0, User.objects.filter_by().count())

    def test_create_user(self):
        self.assertEquals(0, User.objects.filter_by().count())
        data = {'username': 'maigfrga', 'email': 'maigfrga@gmail.com',
                'first_name': 'Manuel', 'last_name': 'Franco'}
        response = self.json_request(self.users_url, data=data)
        self.assertEquals(1, User.objects.filter_by().count())
        json_dict_response = json.loads(response.data)
        self.assertEquals(data['username'], json_dict_response['user']['username'])

    def test_fail_username_unique(self):
        pass

    def test_invalid_access_token(self):
        #test request witouth auth headers
        response = self.json_request(self.users_url, method='put')
        self.assertRegexpMatches(response.data, '.*you do not have access')
        #test request with invalid credentials
        response = self.json_request_with_credentials(self.users_url, method='put',
                                                      username='fake', access_token='123')
        self.assertRegexpMatches(response.data, '.*you do not have access')

    def test_update_user_info(self):
        user = ModelTestFactory.get_user(username='maigfrga')
        response = self.json_request_with_credentials(self.users_url, method='put',
                                                      username=user.username, access_token=user.access_token)
