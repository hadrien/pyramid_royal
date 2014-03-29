from royal.renderer import renderer_adapter

from example.model.user import User
from example.model.photo import Photo

__all__ = ['Photo', 'User']


def includeme(config):
    config.include('pyramid_mongokit')
    config.scan(__name__)


@renderer_adapter('bson.objectid.ObjectId')
def adapt_objectid(o, request):
    return str(o)
