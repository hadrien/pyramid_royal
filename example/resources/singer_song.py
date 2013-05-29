import royal


class Collection(royal.Collection):

    def __getitem__(self, key):
        return Resource(key, self)


class Resource(royal.Resource):
    pass
