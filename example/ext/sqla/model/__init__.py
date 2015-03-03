
from sqlalchemy.engine import engine_from_config

from sqlalchemy.ext.declarative import declarative_base, DeferredReflection
from sqlalchemy.orm import sessionmaker, scoped_session


Session = scoped_session(sessionmaker())


def includeme(config):
    engine = engine_from_config(config.registry.settings)
    Session.configure(bind=engine)
    Base.metadata.bind = engine
    Base.prepare(engine)


class Base(declarative_base(cls=DeferredReflection)):
    __abstract__ = True

    __table_args__ = {
        'mysql_engine': 'InnoDB',
        }
