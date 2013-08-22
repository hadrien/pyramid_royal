import mimetypes

import royal
from royal.exceptions import NotFound

from example.model import Photo


class Collection(royal.Collection):

    def index(self, offset, limit):
        cursor = Photo.get_newests(self.root.db, offset, limit,
                                   author=self.__parent__.__name__)
        query = dict(offset=offset, limit=limit)
        return royal.PaginatedResult(self, cursor, Resource, query,
                                     cursor.count())

    def create(self, **kwargs):
        fs = kwargs['image']
        author = self.__parent__.__name__
        mime_type = mimetypes.guess_extension(fs.filename)
        photo = Photo.create(self.root.db, author, fs.file, mime_type)
        return Resource(str(photo._id), self, photo)


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

    @property
    def links(self):
        return {
            'self': self.root['photos'][self.__name__],
            'author': self.__parent__,
        }
