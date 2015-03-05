import os


import logging

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.schema import DropConstraint, MetaData


log = logging.getLogger(__name__)


mysql_uri = 'mysql+mysqlconnector://root@localhost/royal_test_example'
engine = None


def setupPackage():
    os.environ['MONGO_URI'] = 'mongodb://localhost'
    os.environ['MONGO_DB_NAME'] = 'royal_example'
    os.environ['MONGO_DB_PREFIX'] = ''

    # sqla extentsion setup.
    global engine

    alembic_config = Config()
    alembic_config.set_main_option('script_location',
                                   'example/ext/sqla/db')
    alembic_config.set_main_option('sqlalchemy.url', mysql_uri)

    engine = create_engine(mysql_uri)

    try:
        command.downgrade(alembic_config, 'base')
    except:
        log.exception("Migration downgrade failed, clearing all tables")
        metadata = MetaData(engine)
        metadata.reflect()
        for table in metadata.tables.values():
            for fk in table.foreign_keys:
                engine.execute(DropConstraint(fk.constraint))
        metadata.drop_all()

    command.upgrade(alembic_config, 'head')
