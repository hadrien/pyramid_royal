import logging

from pyramid.location import lineage
import royal
from sqlalchemy.orm.collections import MappedCollection

log = logging.getLogger(__name__)


def includeme(config):
    config.scan(__name__)


class Collection(royal.Collection):

    """
        SessionWrapper is a thin wrapper around SA Session object,
        implementing a possibly advanced (e.g better error handling)
        commit and flush methods.

        A simple implementation would be

        class SessionWrapper:

            Session = Session

            @staticmethod
            def commit():
                Session.commit()

            @staticmethod
            def flush():
                Session.flush()
    """
    SessionWrapper = None

    """
        entity_cls is an SA entity mapped class.
    """
    entity_cls = None

    def __init__(self, name, parent, entities=None):
        super(Collection, self).__init__(name, parent)
        self.entities = entities

    def __repr__(self):
        return '<%s collection at %s named %r>' % (self.__class__.__name__,
                                                   id(self),
                                                   self.name)

    def load_entities(self):
        session = self.SessionWrapper.Session
        self.entities = session.query(self.entity_cls).all()
        # TODO pagination

    def index(self, params):
        if self.entities is None:
            self.load_entities()
        return self

    def create(self, params):
        session = self.SessionWrapper.Session
        entity = self.entity_cls(**params)
        session.add(entity)
        try:
            self.SessionWrapper.flush()
        except Exception:
            log.exception('create resource=%r params=%r', self, params)
            raise
        item = self[entity.id]
        item.entity = entity
        self.SessionWrapper.commit()
        return item


class Item(royal.Item):

    SessionWrapper = None

    # In derived Item classes, specify a model class for singular resources
    # that don't belong to a collection. Otherwise, it will be determined from
    # the parent resource.
    entity_cls = None

    def __init__(self, name, parent, entity=None):
        super(Item, self).__init__(name, parent)
        self.entity = entity
        if self.entity_cls is None and self.parent is not None:
            self.entity_cls = self.parent.entity_cls

    def __repr__(self):
        return '<%s item at %s named %r>' % (self.__class__.__name__,
                                             id(self),
                                             self.name)

    def on_traversing(self, key):
        self.load_entity()

    def load_entity(self):
        session = self.SessionWrapper.Session
        if self.entity is None:
            if self.entity_cls is None:
                raise royal.exceptions.NotFound(self)

            # FIXME Naively assume that entity's PK is the list of resource
            # __name__ in reversed lineage so PK of /slots/123/symbols/456 is
            # (123, 456). Should also be adapted to support resources
            # identified by name.
            pk = [item.name for item in lineage(self)
                  if hasattr(item, 'name')
                  and item.name
                  and not isinstance(item, Collection)]
            pk.reverse()
            self.entity = session.query(self.entity_cls).get(pk)
            if self.entity is None:
                royal.exceptions.NotFound(self)

        return self.entity

    def show(self, params):
        self.load_entity()
        return self

    def delete(self):
        self.load_entity().delete()
        self.SessionWrapper.commit()

    def update(self, params):
        params_copy = params.copy()
        entity = self.load_entity()
        # Ignore parameters that are part of primary key.
        [params_copy.pop(pk.name, '') for pk in entity.__mapper__.primary_key]
        for param in params_copy:
            try:
                getattr(entity, param)
                setattr(entity, param, params_copy[param])
            except AttributeError:
                pass
        try:
            self.SessionWrapper.commit()
        except Exception:
            log.exception('update resource=%r params=%r', self, params)
            raise
        return entity


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
