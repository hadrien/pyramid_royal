from pyramid.events import NewRequest

from royal.declarative import collection_config, item_config
from royal.renderer import renderer_adapter
from royal.resource import Root, Collection, Item, find_item, find_collection
from royal.deserializer import deserializer_config


__all__ = [
    'Collection',
    'collection_config',
    'deserializer_config',
    'find_collection',
    'find_item',
    'Item',
    'item_config',
    'renderer_adapter',
    'Root',
]


def includeme(config):
    config.include('royal.renderer')
    config.include('royal.deserializer')
    config.include('royal.directives')
    config.include('royal.resource')
    config.include('royal.views')

    config.add_subscriber_predicate(
        'request_methods',
        RequestMethodEventPredicate
    )

    config.add_subscriber(
        override_request_method,
        NewRequest,
        request_methods=['POST'],
    )
    config.add_request_method(is_resource_nested, 'is_nested')
    config.commit()


def is_resource_nested(request, resource):
    """Return True if resource is nested in another resource representation.

    It permits to vary a resource representation.
    """
    return request.context not in [resource, resource.__parent__]


class RequestMethodEventPredicate(object):

    def __init__(self, methods, config):
        self.methods = methods
        self.phash = self.text

    def __call__(self, event):
        return event.request.method in self.methods

    def text(self):
        return 'request_method in %s' % self.methods


def override_request_method(event):
    methods = ['PUT', 'DELETE']
    override = (
        event.request.headers.get('X-HTTP-Method-Override') or
        event.request.POST.get('_method', '').upper()
    )
    if override in methods:
        event.request.method = override
