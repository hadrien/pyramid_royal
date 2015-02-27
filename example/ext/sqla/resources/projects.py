from . import CollectionBase, ItemBase

from example.model import User


class Collection(CollectionBase):
    entity_cls = User


class Item(ItemBase):
    entity_cls = User
