import functools


class _DummyResourceBase(object):

    def __init__(self, name, parent, request, resource_path, resource_type,
                 **kw):
        self.__name__ = self.name = name
        self.__parent__ = parent
        self.__resource_path__ = resource_path
        self.__resource_type__ = resource_type
        self.__dict__.update(kw)


DummyCollection = functools.partial(_DummyResourceBase,
                                    resource_type='Collection')

DummyItem = functools.partial(_DummyResourceBase, resource_type='Item')
