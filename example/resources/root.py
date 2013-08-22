import royal

from pyramid.decorator import reify

from example.resources import user
from example.resources import photo


class Root(royal.Root):

    children = {
        'users': user.Collection,
        'photos': photo.Collection,
        }

    def __getitem__(self, key):
        return self.children[key](key, self)

    @reify
    def db(self):
        return self.request.mongo_connection.get_db()
