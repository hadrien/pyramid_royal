from pyramid.events import NewRequest

from royal.renderer import renderer_adapter
from royal.resource import Root, Collection, Item
from royal.deserializer import deserializer_config


__all__ = [
    'Collection',
    'deserializer_config',
    'Item',
    'renderer_adapter',
    'Root',
]


def includeme(config):
    config.include('royal.renderer')
    config.include('royal.deserializer')
    config.include('royal.utility')
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

    config.commit()


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
