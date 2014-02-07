from example.model.user import User
from example.model.photo import Photo


def includeme(config):
    config.include('pyramid_mongokit')

    config.register_document(User)
    config.generate_index(User)

    config.register_document(Photo)
    config.generate_index(Photo)
