import unittest


class ApiBaseTestCase(unittest.TestCase):
    def setUp(self):
        import users.views
        self.client = users.views.app.test_client()

    def tearDown(self):
        pass

