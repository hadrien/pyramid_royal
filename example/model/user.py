from example.model import base

from pyramid_mongokit import register


@register()
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

    @staticmethod
    def replace(db, username, new_username, new_email):
        spec = {'username': username}
        update = {
            '$set': {
                'username': new_username,
                'email': new_email,
            },
        }
        user = db.User.find_and_modify(spec, update, new=True)
        return user
