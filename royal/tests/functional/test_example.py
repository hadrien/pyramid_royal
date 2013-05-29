import sys
import unittest

import webtest

from pyramid import testing


class TestExample(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('example')
        self.config.commit()
        self.app = webtest.TestApp(self.config.make_wsgi_app())

    def tearDown(self):
        testing.tearDown()
        for m in list(sys.modules):
            if 'example' in m:
                del sys.modules[m]
