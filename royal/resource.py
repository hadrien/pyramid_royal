from zope.interface import implementer

from pyramid.decorator import reify
from pyramid.traversal import find_root

from royal import exceptions
from royal.interfaces import (
    IBase,
    ICollection,
    IItem,
    IRoot,
)


def includeme(config):
    config.set_root_factory(Root)


@implementer(IBase)
class Base(object):

    def __init__(self, name, parent):
        self.__name__ = unicode(name)
        self.__parent__ = parent
        if not hasattr(self, 'children'):
            self.children = {}

    def __getitem__(self, key):
        key = unicode(key)
        self.on_traversing(key)
        return self.children[key](key, self)

    def _not_allowed(self, name):
        raise exceptions.MethodNotAllowed(self, name)

    @property
    def index(self):
        self._not_allowed('index')

    @property
    def create(self):
        self._not_allowed('create')

    @property
    def show(self):
        self._not_allowed('show')

    @property
    def replace(self):
        self._not_allowed('replace')

    @property
    def update(self):
        self._not_allowed('update')

    @property
    def delete(self):
        self._not_allowed('delete')

    @reify
    def root(self):
        return find_root(self)

    def resource_url(self, resource, **query_params):
        kw = {'query': query_params}
        return self.root.request.resource_url(resource, **kw)

    def url(self, **query_params):
        return self.resource_url(self, **query_params)

    @property
    def parent(self):
        return self.__parent__

    @property
    def name(self):
        return self.__name__

    @property
    def links(self):
        _links = {name: {'href': cls(name, self).url()}
                  for name, cls in self.children.iteritems()}
        _links['href'] = self.url()
        return _links

    def on_traversing(self, key):
        pass


@implementer(IRoot)
class Root(Base):
    children = {}
    request = None

    def __init__(self, request):
        super(Root, self).__init__('', None)
        self.request = request

    def show(self, params):
        return self.links


@implementer(IItem)
class Item(Base):
    pass


@implementer(ICollection)
class Collection(Base):

    def __getitem__(self, key):
        self.on_traversing(key)
        if hasattr(self, 'item_cls'):
            return self.item_cls(key, self)
        return self.children[key](key, self)
