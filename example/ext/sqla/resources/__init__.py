import logging


from ..model import Session

from royal.ext.sqla import Collection as SACollection
from royal.ext.sqla import Item as SAItem

log = logging.getLogger(__name__)

from pyramid.tweens import EXCVIEW


class CollectionBase(SACollection):
    Session = Session


class ItemBase(SAItem):
    Session = Session


def includeme(config):

    config.add_resource('projects')
    config.add_tween('example.ext.sqla.resources.session_tween_factory',
                     under=EXCVIEW)
    config.scan(__name__)


def remove_session(request):
    Session.remove()


def session_tween_factory(handler, registry):
    def session_tween(request):
        request.add_finished_callback(remove_session)
        response = handler(request)
        return response
    return session_tween
