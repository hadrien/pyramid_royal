class DummyResourceBase(dict):
    def __init__(self, name, parent, request,
                 resource_path, resource_type,
                 **kwargs):
        self.__name__ = name
        self.__parent__ = parent
        self.__resource_path__ = resource_path
        self.__resource_type__ = resource_type
        self.name = name
        self.__dict__.update(kwargs)


class DummyCollection(DummyResourceBase):
    def __init__(self, name, parent, request, resource_path, **kwargs):
        super(DummyCollection, self).__init__(
            name, parent, request,
            resource_path, resource_type='Collection',
            **kwargs)

class DummyItem(DummyResourceBase):
    def __init__(self, name, parent, request, resource_path, **kwargs):
        super(DummyItem, self).__init__(
            name, parent, request,
            resource_path, resource_type='Item',
            **kwargs)
