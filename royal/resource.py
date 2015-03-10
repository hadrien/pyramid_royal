from zope.interface import implementer

from pyramid.decorator import reify
from pyramid.location import lineage
from pyramid.traversal import find_root, find_interface

from royal import exceptions
from royal.interfaces import (
    IBase,
    ICollection,
    IItem,
    IRoot,
)


def includeme(config):
    config.set_root_factory(Root)


def _find_resource(resource, resource_path, resource_type):
    test = lambda arg: (arg.__resource_path__ == resource_path and
                        arg.__resource_type__ == resource_type)

    for location in lineage(resource):
        try:
            if test(location):
                return location
        except AttributeError:
            continue


def find_collection(resource, resource_path):
    return _find_resource(resource, resource_path, 'Collection')


def find_item(resource, resource_path):
    return _find_resource(resource, resource_path, 'Item')


@implementer(IBase)
class Base(object):

    __children__ = None

    def __init__(self, name, parent, request):
        self.__name__ = unicode(name)
        self.__parent__ = parent
        self.request = request

    def __getitem__(self, key):
        key = unicode(key)
        self.on_traversing(key)
        try:
            return self.__children__[key](key, self, self.request)
        except TypeError:
            raise KeyError(key)

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

    def find_interface(self, interface):
        return find_interface(self, interface)

    def find_collection(self, resource_path):
        return find_collection(self, resource_path)

    def find_item(self, resource_path):
        return find_item(self, resource_path)

    def resource_url(self, resource, **query_params):
        kw = {'query': query_params}
        return self.request.resource_url(resource, **kw)

    def url(self, **query_params):
        return self.resource_url(self, **query_params)

    @property
    def name(self):
        return self.__name__

    @property
    def links(self):
        links = ({name: self.resource_url(cls(name, self, self.request))
                  for name, cls in self.__children__.iteritems()}
                 if self.__children__
                 else {}
                 )
        links['self'] = self.url()
        return links

    def on_traversing(self, key):
        pass


@implementer(IRoot)
class Root(Base):
    __children__ = {}
    request = None

    def __init__(self, request):
        super(Root, self).__init__('', None, request)

    def show(self, params):
        return self.links


@implementer(IItem)
class Item(Base):
    pass


@implementer(ICollection)
class Collection(Base):

    def __getitem__(self, key):
        self.on_traversing(key)
        try:
            return self.item_cls(key, self, self.request)
        except AttributeError:
            raise KeyError(key)
