from zope.interface import implementer

from pyramid.decorator import reify
from pyramid.traversal import find_root

from royal import exceptions as exc
from royal.interfaces import (
    IBase,
    ICollection,
    IPaginatedResult,
    IResource,
    IRoot,
    )


@implementer(IBase)
class Base(object):

    def __init__(self, name, parent):
        self.__name__ = name
        self.__parent__ = parent

    @reify
    def root(self):
        return find_root(self)

    @property
    def links(self):
        return {'self': self}


@implementer(IRoot)
class Root(Base):
    children = {}

    def __init__(self, request):
        super(Root, self).__init__('', None)
        self.request = request

    def show(self):
        return None

    @property
    def links(self):
        return dict((name, cls(name, self))
                    for name, cls in self.children.iteritems())


@implementer(IResource)
class Resource(Base):

    def show(self):
        raise exc.MethodNotAllowed(self)

    def put(self):
        raise exc.MethodNotAllowed(self)

    def patch(self):
        raise exc.MethodNotAllowed(self)

    def delete(self):
        raise exc.MethodNotAllowed(self)

    @reify
    def resource_name(self):
        """Resource name used at rendering phase.
        By default, it is collection name without last s.
        """
        if self.__parent__ is not None:
            return self.__parent__.__name__[0:-1]
        return self.__name__

    @property
    def links(self):
        return {'self': self}


@implementer(ICollection)
class Collection(Base):

    def index(self, *args, **kwargs):
        raise exc.MethodNotAllowed(self)

    def create(self, params):
        raise exc.MethodNotAllowed(self)

    def delete(self):
        raise exc.MethodNotAllowed(self)


@implementer(IPaginatedResult)
class PaginatedResult(object):

    def __init__(self, parent, iterator, resource_cls, query, total):
        self.parent = parent
        self.iterator = iterator
        self.resource_cls = resource_cls
        self.query = query
        self.total = total

    def __iter__(self):
        for item in self.iterator:
            yield self.resource_cls(item._id, self.parent, model=item)
