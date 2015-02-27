from . import CollectionBase, ItemBase

from ..model.project import Project


class Collection(CollectionBase):
    entity_cls = Project


class Item(ItemBase):
    entity_cls = Project
