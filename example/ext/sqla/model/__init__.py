import logging

from pyramid.events import subscriber
from sqlalchemy.exc import InvalidRequestError, DBAPIError

from .meta import Session
from .project import Project

log = logging.getLogger(__name__)

__all__ = ['Project', 'Session']


def includeme(config):
    config.include('.meta')


def commit_session(request):
    if request.exception:
        try:
            Session.rollback()
        except:
            log.exception('Session.rollback failed on %s', Session)
            raise
        finally:
            Session.remove()
    else:
        try:
            Session.commit()

        except InvalidRequestError:
            log.debug('Nothing to commit for session %s', Session,
                      exc_info=True)

        except DBAPIError:
            log.exception('Session.commit failed on %s', Session)
            Session.rollback()
            raise

        finally:
            Session.remove()


@subscriber('pyramid.events.NewRequest')
def on_new_request(event):
    event.request.add_finished_callback(commit_session)
