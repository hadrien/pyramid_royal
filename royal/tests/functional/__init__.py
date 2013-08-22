import os
import logging

from pyramid_mongokit import SingleDbConnection

from example.model import User

log = logging.getLogger(__name__)


def setup_package():
    os.environ['MONGO_URI'] = 'mongodb://localhost'
    os.environ['MONGO_DB_NAME'] = 'royal_example'

    connection = new_connection()
    setup_example_fixtures(connection)
    connection.close()


def teardown_package():
    connection = new_connection()
    for name in connection.db.collection_names():
        if u'system.indexes' not in name:
            connection.db[name].remove()
    connection.close()


def new_connection():
    db_prefix = ''
    return SingleDbConnection(os.environ['MONGO_DB_NAME'], db_prefix,
                              os.environ['MONGO_URI'])


def setup_example_fixtures(connection):
    connection.register(User)
    connection.generate_index(User)
    try:
        User.create(connection.db, u'hadrien', u'hadrien@ectobal.com')
    except Exception:
        log.exception('setup fixture failed')
