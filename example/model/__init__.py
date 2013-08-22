from pyramid_mongokit import register_document, generate_index

from example.model.user import User
from example.model.photo import Photo


def includeme(config):
    config.include('pyramid_mongokit')

    register_document(config.registry, User)
    generate_index(config.registry, User)

    register_document(config.registry, Photo)
    generate_index(config.registry, Photo)
