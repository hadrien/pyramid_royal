import mongokit

from bson.objectid import ObjectId
from pymongo import DESCENDING


class Document(mongokit.Document):

    use_dot_notation = True

    @classmethod
    def get_newests(cls, db, offset, limit, **kwargs):
        # do not use skip on anything on production!
        collection = db[cls.__name__]
        return (
            collection.find(kwargs)
                      .sort('_id', DESCENDING)
                      .limit(limit)
                      .skip(offset)
        )

    @classmethod
    def get_by(cls, db, **kw):
        collection = db[cls.__name__]
        return collection.find(kw)

    @classmethod
    def get_one(cls, db, **kw):
        collection = db[cls.__name__]
        return collection.find_one(kw)

    @classmethod
    def get_by_id(cls, db, _id):
        if not isinstance(_id, ObjectId):
            _id = ObjectId(_id)
        collection = db[cls.__name__]
        return collection.find_one({_id: _id})

    @classmethod
    def delete_one(cls, db, **kw):
        collection = db[cls.__collection__]
        return collection.remove(kw, multi=False)
