"""Boilerplate code for using royal with SQLAlchemy
"""
import logging

from pyramid.location import lineage
from sqlalchemy.orm.collections import MappedCollection

import royal

log = logging.getLogger(__name__)


def includeme(config):
    config.scan(__name__)


class Collection(royal.Collection):

    """
        Session is an SA session.
    """
    Session = None

    """
        entity_cls is an SA entity mapped class.
    """
    entity_cls = None

    def __init__(self, name, parent, request, entities=None):
        super(Collection, self).__init__(name, parent, request)
        self.entities = entities

    def load_entities(self):
        self.entities = self.Session.query(self.entity_cls).all()
        # TODO pagination

    def index(self, params):
        if self.entities is None:
            self.load_entities()
        return self

    def create(self, params):
        entity = self.entity_cls(**params)
        self.Session.add(entity)
        try:
            self.Session.flush()
        except:
            log.exception('create resource=%r params=%r', self, params)
            raise
        item = self[entity.id]
        item.entity = entity
        return item


class Item(royal.Item):

    Session = None

    # In derived Item classes, specify a model class for singular resources
    # that don't belong to a collection. Otherwise, it will be determined from
    # the parent resource.
    entity_cls = None

    def __init__(self, name, parent, request, entity=None):
        super(Item, self).__init__(name, parent, request)
        self.entity = entity
        if self.entity_cls is None:
            try:
                self.entity_cls = self.__parent__.entity_cls
            except AttributeError:
                pass

    def _get_primary_key(self):
        # FIXME Naively assume that entity's PK is the list of resource
        # __name__ in reversed lineage so PK of /users/123/photos/456 is
        # (123, 456). Should also be adapted to support resources
        # identified by name.
        pk = [item.name for item in lineage(self)
              if hasattr(item, 'name')
              and item.name
              and not isinstance(item, Collection)]
        pk.reverse()
        return pk

    def load_entity(self):
        if self.entity is None:
            if self.entity_cls is None:
                raise royal.exceptions.NotFound(self)
            pk = self._get_primary_key()
            self.entity = self.Session.query(self.entity_cls).get(pk)
            if self.entity is None:
                raise royal.exceptions.NotFound(self)

        return self.entity

    def show(self, params):
        self.load_entity()
        return self

    def delete(self):
        entity = self.load_entity()
        self.Session.delete(entity)

    def update(self, params):
        params_copy = params.copy()
        entity = self.load_entity()
        # Ignore parameters that are part of primary key.
        [params_copy.pop(pk.name, '') for pk in entity.__mapper__.primary_key]
        for param in params_copy:
            if hasattr(entity, param):
                setattr(entity, param, params_copy[param])
        return self

    def replace(self, params):
        try:
            self.load_entity()
        except royal.exceptions.NotFound:
            pk_column_names = [column.name for column
                               in self.entity_cls.__mapper__.primary_key]
            pk_dict = dict(zip(pk_column_names, self._get_primary_key()))
            self.entity = self.entity_cls(**pk_dict)
            self.Session.add(self.entity)
        return self.update(params)


@royal.renderer_adapter(Collection)
def adapt_collection(collection, request):
    items = []
    if collection.entities is None:
        collection.load_entities()
    if isinstance(collection.entities, MappedCollection):
        for item_id, entity in collection.entities.items():
            item = collection[item_id]
            item.entity = entity
            items.append(item)
    else:
        for entity in collection.entities:
            item = collection[entity.id]
            item.entity = entity
            items.append(item)
    return {
        u'items': items,
        u'links': collection.links,
    }


def render_hyperlink(item):
    try:
        return {'id': int(item.name)}
    except ValueError:
        return {'id': item.name}


def render_model(item):
    entity = item.load_entity()
    columns = entity.__table__.columns
    return {column.name: getattr(entity, column.name) for column in columns}


@royal.renderer_adapter(Item)
def adapt_item(item, request):
    if request.is_nested(item):
        result = render_hyperlink(item)
    else:
        result = render_model(item)
    result['links'] = item.links
    return result
