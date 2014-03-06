import royal

from voluptuous import Schema, Required, Coerce, All, Range
from royal.exceptions import NotFound

from example.model import User, Photo


class Collection(royal.Collection):

    index_schema = Schema({
        Required('offset', default=0): All(Coerce(int), Range(min=0)),
        Required('limit', default=20): All(Coerce(int), Range(min=1, max=50)),
    })

    def index(self, params):
        offset = params['offset']
        limit = params['limit']
        cursor = User.get_newests(self.root.db, offset, limit)
        documents = [Item(user.username, self, user).show() for user in cursor]
        result = {
            'users': documents,
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


class Item(royal.Item):

    def __init__(self, key, parent, document=None):
        super(Item, self).__init__(key, parent)
        self.document = document

    def load_document(self):
        if self.document is None:
            self.document = User.get_one(self.root.db, username=self.name)
        if self.document is None:
            raise NotFound(self)
        return self.document

    def on_traversing(self, key):
        self.load_document()

    def show(self, params=None):
        user = self.load_document()
        user['href'] = self.url()
        user['photos'] = {
            'href': self['photos'].url(),
        }
        return user

    def replace(self, params):
        new_username = params['username']
        new_email = params['email']
        user = User.replace(self.root.db, self.name,
                            new_username=new_username,
                            new_email=new_email)
        Photo.replace_author(self.root.db, self.name, new_username)
        new_item = Item(new_username, self.parent, user)
        user['href'] = new_item.url()
        user['photos'] = {
            'href': new_item['photos'].url()
        }
        return user
