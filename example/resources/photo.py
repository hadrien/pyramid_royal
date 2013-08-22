import royal
from royal.exceptions import NotFound

from example.model import Photo


class Collection(royal.Collection):

    def __getitem__(self, key):
        return Resource(key, self)

    def index(self, offset, limit):
        cursor = Photo.get_newests(self.root.db, offset, limit)
        query = dict(offset=offset, limit=limit)
        return royal.PaginatedResult(self, cursor, Resource, query,
                                     cursor.count())


class Resource(royal.Resource):

    def __init__(self, key, parent, model=None):
        super(Resource, self).__init__(key, parent)
        self.model = model

    def load_model(self):
        if self.model is None:
            self.model = self.root.db.get_by(_id=self.__name__).first()
        if self.model is None:
            raise NotFound(self)
        return self.model

    def show(self):
        return self.load_model()
