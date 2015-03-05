from royal.ext.sqla import Collection as SACollection
from royal.ext.sqla import Item as SAItem

from ..model import Session


class CollectionBase(SACollection):
    Session = Session


class ItemBase(SAItem):
    Session = Session


def includeme(config):
    config.add_resource('projects')
