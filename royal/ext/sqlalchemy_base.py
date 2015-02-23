import logging

from pyramid.location import lineage
import royal
from sqlalchemy.orm.collections import MappedCollection

log = logging.getLogger(__name__)


# class LinksMixin(object):

#     @property
#     def links(self):
#         links = {name: self.root.request.resource_url(self, name)
#                  for name in self.children}
#         links['self'] = self.url()
#         return links


class Collection(royal.Collection):
    sa_model = None
    sa_exceptions = None
    entity_cls = None

    def __init__(self, name, parent, entities=None):
        super(Collection, self).__init__(name, parent)
        self.entities = entities

    def __repr__(self):
        return '<%s collection at %s named %r>' % (self.__class__.__name__,
                                                   id(self),
                                                   self.name)

    def load_entities(self):
        self.entities = self.entity_cls.all()

    def index(self, params):
        if self.entities is None:
            self.load_entities()
        return self

    def create(self, params):
        entity = self.entity_cls(**params)
        entity.save()
        try:
            self.sa_model.flush()
        except self.sa_exceptions.DuplicatedEntity:
            raise
        except Exception:
            log.exception('create resource=%r params=%r', self, params)
            raise
        item = self[entity.id]
        item.entity = entity
        self.sa_model.commit()
        return item


class Item(royal.Item):

    sa_model = None
    sa_exceptions = None

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
            try:
                self.entity = self.entity_cls.get(pk)
            except KeyError:
                raise royal.exceptions.NotFound(self)

        return self.entity

    def show(self, params):
        self.load_entity()
        return self

    def delete(self):
        self.load_entity().delete()
        self.sa_model.commit()

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
            self.sa_model.commit()
        except self.sa_exceptions.DuplicatedEntity:
            raise
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
