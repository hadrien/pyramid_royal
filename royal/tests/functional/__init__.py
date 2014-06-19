import os
import logging
import unittest

import webtest

from pyramid.config import Configurator
from pyramid.decorator import reify
from pyramid_mongokit import SingleDbConnection

log = logging.getLogger(__name__)


def setup_package():
    connection = new_connection()
    setup_example_fixtures(connection)
    connection.close()


def teardown_package():
    connection = new_connection()
    for name in connection.db.collection_names():
        if u'system.indexes' not in name:
            connection.db[name].remove()
    connection.close()


class TestBase(unittest.TestCase):

    maxDiff = None

    @reify
    def config(self):
        _config = Configurator(settings={})
        _config.include('example')
        self.addCleanup(delattr, self, 'config')
        return _config

    @reify
    def app(self):
        self.addCleanup(delattr, self, 'app')
        return webtest.TestApp(self.config.make_wsgi_app())

    @reify
    def db(self):
        self._db = new_connection()
        self.addCleanup(self._db.close)
        self.addCleanup(delattr, self, 'db')
        return self._db.get_db()


def new_connection():
    from example.model import User, Photo
    db_prefix = ''
    connection = SingleDbConnection(os.environ['MONGO_DB_NAME'], db_prefix,
                                    os.environ['MONGO_URI'])
    connection.register(User)
    connection.register(Photo)
    connection.generate_index(User)
    connection.generate_index(Photo)
    return connection


def setup_example_fixtures(connection):
    from example.model import User

    try:
        User.create(connection.db, u'hadrien', u'hadrien@ectobal.com')
    except Exception:
        log.exception('setup fixture failed')
