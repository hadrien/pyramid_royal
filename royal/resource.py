import onctuous

from pyramid.decorator import reify
from pyramid.traversal import find_root

from royal import exceptions as exc


class Base(object):

    def __init__(self, name, parent, model=None):
        self.__name__ = name
        self.__parent__ = parent
        self.model = model

        self.ancestors = {}

        has_parent_ancestors = (parent is not None
                                and parent.ancestors is not None)

        if has_parent_ancestors:
            self.ancestors.update(parent.new_ancestors())

        is_collection = isinstance(self, Collection)

        if is_collection:
            self.collection_name = name
        else:
            parent_is_collection = parent and isinstance(parent, Collection)
            if parent_is_collection:
                self.collection_name = parent.__name__
            else:
                self.collection_name = name

    @reify
    def root(self):
        return find_root(self)

    @property
    def db(self):
        return self.request.mongo_db

    @reify
    def request(self):
        return self.root.request

    def new_ancestors(self):
        ancestors = self.ancestors.copy()
        if isinstance(self, Resource):
            ancestors[self.collection_name] = self
        return ancestors

    @property
    def links(self):
        return {'self': self}


class Root(Base):

    def __init__(self, request):
        super(Root, self).__init__('', None)
        self.request = request


class Resource(Base):

    def show(self):
        raise exc.MethodNotAllowed(self)

    def put(self):
        raise exc.MethodNotAllowed(self)

    def patch(self):
        raise exc.MethodNotAllowed(self)

    def delete(self):
        raise exc.MethodNotAllowed(self)

    @property
    def resource_name(self):
        return self.collection_name[0:-1]

    @property
    def links(self):
        return {'self': self}


class Collection(Base):

    @property
    def resource_name(self):
        return self.collection_name

    index = None

    def create(self, params):
        raise exc.MethodNotAllowed(self)

    def delete(self):
        raise exc.MethodNotAllowed(self)


class PaginatedResult(object):

    def __init__(self, parent, iterator, resource_cls, total):
        self.parent = parent
        self.iterator = iterator
        self.resource_cls = resource_cls
        self.total = total

    def __iter__(self):
        return self.next()

    def next(self):
        item = self.iterator.next()
        yield self.resource_cls(item._id, self.parent, model=item)
