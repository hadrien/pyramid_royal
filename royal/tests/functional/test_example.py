import unittest
import pkg_resources
import webtest

from pyramid.config import Configurator
from pyramid.decorator import reify


class Test(unittest.TestCase):

    @reify
    def config(self):
        from example import includeme
        _config = Configurator(settings={})
        _config.include(includeme)
        self.addCleanup(delattr, self, 'config')
        return _config

    @reify
    def app(self):
        self.addCleanup(delattr, self, 'app')
        return webtest.TestApp(self.config.make_wsgi_app())

    def test_root(self):
        self.app.get('/')

    def test_users_index(self):
        self.app.get('/users')

    def test_post_photo(self):
        image_gif = pkg_resources.resource_stream('royal.tests.functional',
                                                  'image.gif')
        result = self.app.post(
            '/users/hadrien/photos',
            upload_files=[(u'image', u'image.gif', image_gif.read())]
            )
