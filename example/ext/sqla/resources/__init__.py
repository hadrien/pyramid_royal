import logging


from ..model import Session

from royal.ext.sqla import Collection as SACollection
from royal.ext.sqla import Item as SAItem

log = logging.getLogger(__name__)


class CollectionBase(SACollection):
    Session = Session


class ItemBase(SAItem):
    Session = Session


def includeme(config):

    config.add_resource('projects')
    config.scan(__name__)
