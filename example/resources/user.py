import royal
from royal.exceptions import NotFound

from example.model import User

from example.resources import user_photo


class Collection(royal.Collection):

    def __getitem__(self, key):
        return Resource(key, self)

    def index(self, offset, limit):
        cursor = User.get_newests(self.root.db, offset, limit)
        query = dict(offset=offset, limit=limit)
        return royal.PaginatedResult(self, cursor, Resource, query,
                                     cursor.count())


class Resource(royal.Resource):

    children = {
        'photos': user_photo.Collection,
        }

    def __init__(self, key, parent, model=None):
        super(Resource, self).__init__(key, parent)
        self.model = model

    def __getitem__(self, key):
        return self.children[key](key, self)

    def load_model(self):
        if self.model is None:
            self.model = self.root.db.get_by(username=self.__name__).first()
        if self.model is None:
            raise NotFound(self)
        return self.model

    def show(self):
        return self.load_model()
