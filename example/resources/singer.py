import royal

from . import singer_song


class Collection(royal.Collection):

    def __getitem__(self, key):
        return Resource(key, self)


class Resource(royal.Resource):

    children = {
        'songs': singer_song.Collection,
        }

    def __getitem__(self, key):
        return self.children[key](key, self)

    def show(self):
        return {'singer': self.__name__}
