import functools

from pyramid.testing import DummyResource


class _DummyResourceBase(DummyResource):

    def __init__(self, name, parent, request, resource_path, resource_type,
                 **kw):
        super(_DummyResourceBase, self).__init__(
            name,
            parent,
            request=request,
            **kw
            )
        self.name = name
        self.parent = parent
        self.__resource_path__ = resource_path
        self.__resource_type__ = resource_type


DummyCollection = functools.partial(_DummyResourceBase,
                                    resource_type='Collection')

DummyItem = functools.partial(_DummyResourceBase, resource_type='Item')
