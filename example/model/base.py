import mongokit

from pymongo import DESCENDING


class Document(mongokit.Document):

    use_dot_notation = True

    @classmethod
    def get_newests(cls, db, offset, limit):
        skip = offset * limit
        collection = db[cls.__name__]
        return (
            collection.find()
                      .sort('_id', DESCENDING)
                      .limit(limit)
                      .skip(skip)
        )
