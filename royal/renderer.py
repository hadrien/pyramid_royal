import logging
from collections import OrderedDict

import venusian
from pyramid.interfaces import IRendererFactory
from pyramid.renderers import JSON as pyramid_JSON
from zope.interface import implementer

from royal.interfaces import IAdaptableRenderer

log = logging.getLogger(__name__)


def includeme(config):
    config.add_renderer('royal', Factory)

    config.registry.registerUtility(JSON())

    config.add_directive('add_renderer_adapter', add_renderer_adapter)

    config.scan(__name__)


@implementer(IRendererFactory)
class Factory(object):
    """ Constructor: info will be an oect having the
    following attributes: name (the renderer name), package
    (the package that was 'current' at the time the
    renderer was registered), type (the renderer type
    name), registry (the current application registry) and
    settings (the deployment settings dictionary). """

    default_match = 'application/json'

    formatters = None

    def __init__(self, info):
        self.info = info

        self.formatters = OrderedDict([
            ('application/json',
             info.registry.getUtility(IAdaptableRenderer)(info)),
        ])

    def __call__(self, value, system):
        """ Call the renderer implementation with the value
        and the system value passed in as arguments and return
        the result (a string or unicode oect).  The value is
        the return value of a view.  The system value is a
        dictionary containing available system values
        # (e.g. view, context, and request). """
        request = system['request']
        format = request.accept.best_match(self.formatters.keys(),
                                           default_match=self.default_match)
        request.response.content_type = format
        return self.formatters[format](value, system)


@implementer(IAdaptableRenderer)
class JSON(pyramid_JSON):
    pass


def add_renderer_adapter(config, dotted_name, adapter):

    def callback():
        (config.registry.getUtility(IAdaptableRenderer)
                        .add_adapter(adapted, adapter))

    adapted = config.maybe_dotted(dotted_name)

    intr = config.introspectable(
        category_name='Renderer adapters',
        discriminator=adapted,
        title=adapted,
        type_name='',
    )
    intr['adapter'] = adapter

    config.action(adapted, callback, introspectables=(intr, ))


class renderer_adapter(object):
    """A decorator to add a rendered adapter"""

    def __init__(self, type_or_iface):
        self.type_or_iface = type_or_iface

    def __call__(self, wrapped):

        def callback(context, name, ob):
            config = context.config.with_package(info.module)
            config.add_renderer_adapter(self.type_or_iface, ob, **settings)

        info = venusian.attach(wrapped, callback)
        settings = {'_info': info.codeinfo}
        return wrapped


@renderer_adapter('datetime.date')
@renderer_adapter('datetime.datetime')
def adapt_datetime(o, request):
    return o.isoformat()


@renderer_adapter('decimal.Decimal')
def adapt_decimal(o, request):

    class _number_str(float):
        # kludge to have decimals correctly output as JSON numbers.
        # converting them to strings would cause extra quotes.

        def __init__(self, o):
            self.o = o

        def __repr__(self):
            return str(self.o)

    return _number_str(o)
