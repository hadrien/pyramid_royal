from example.model import base


class User(base.Document):
    __collection__ = 'users'

    structure = {
        u'username': unicode,
        u'email': unicode,
        }

    required = structure.keys()

    indexes = [
        {'fields': u'username', 'unique': True},
        {'fields': u'email', 'unique': True},
        ]

    @staticmethod
    def create(db, username, mail):
        user = db.User()
        user.username = username
        user.email = mail
        user.save()
        return user
