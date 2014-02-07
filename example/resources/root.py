import royal

from pyramid.decorator import reify


class Root(royal.Root):

    @reify
    def db(self):
        return self.request.mongo_connection.get_db()

    def show(self):
        return {
            'users': self['users'].url(),
            'photos': self['photos'].url()
        }
