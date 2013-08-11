from test.models import *
from test.views import *
def init_test():
    import unittest
    suite1 = unittest.TestLoader().loadTestsFromTestCase(UserModelTestCase)
    suite2 = unittest.TestLoader().loadTestsFromTestCase(UserViewsTestCase)
    alltests = unittest.TestSuite([suite1, suite2])
    unittest.TextTestRunner(verbosity=2).run(alltests)
