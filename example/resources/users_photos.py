import mimetypes

import royal

from example.model import Photo
from example.resources import photos


class Collection(royal.Collection):

    def index(self, offset=0, limit=10):
        cursor = Photo.get_newests(self.root.db, offset, limit,
                                   author=self.parent.name)
        documents = [photos.Item(str(doc._id), self.root, doc).show()
                     for doc in cursor]
        result = {
            'photos': documents,
            'href': self.url(offset=offset, limit=limit),
            'first': self.url(offset=0, limit=limit),
        }
        has_previous = offset > 0
        if has_previous:
            result['previous'] = self.url(offset=max(offset - limit, 0),
                                          limit=limit)
        has_next = len(documents) == limit
        if has_next:
            result['next'] = self.url(offset=offset + limit, limit=limit)
        return result

    def create(self, params):
        fs = params['image']
        author = self.parent.name
        mime_type = mimetypes.guess_extension(fs.filename)
        doc = Photo.create(self.root.db, author, fs.file, mime_type)
        return photos.Item(str(doc._id), self.root['photos'], doc)
