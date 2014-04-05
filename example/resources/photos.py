import royal

from royal.exceptions import NotFound
from voluptuous import Schema, Required, Coerce, All, Range

from example.model import Photo


class Collection(royal.Collection):

    index_schema = Schema({
        Required('offset', default=0): All(Coerce(int), Range(min=0)),
        Required('limit', default=20): All(Coerce(int), Range(min=1, max=50)),
    })

    def index(self, params):
        offset = params['offset']
        limit = params['limit']
        cursor = Photo.get_newests(self.root.db, offset, limit)
        query = dict(offset=offset, limit=limit)
        return royal.PaginatedResult(self, cursor, Item, query,
                                     cursor.count())


class Item(royal.Item):

    def __init__(self, key, parent, document=None):
        super(Item, self).__init__(key, parent)
        self.document = document

    def load_document(self):
        if self.document is None:
            self.document = Photo.get_by_id(self.root.db, self.__name__)

        if self.document is None:
            raise NotFound(self)

        return self.document

    def show(self, params=None):
        result = self.load_document()
        author_username = result['author']
        result['href'] = self.url()
        result['author'] = {
            'href': self.root['users'][author_username].url()
        }
        return result


@royal.renderer_adapter(Item)
def adapt_item(item, request):
    return item.show()
