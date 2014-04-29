import json
from decimal import Decimal

import venusian
from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPException,
    HTTPUnsupportedMediaType,
)

from webob.multidict import NoVars, MultiDict
from zope.interface import implementer

from royal.interfaces import IDeserializer


def includeme(config):
    utility = Utility()
    config.registry.registerUtility(utility)
    config.add_directive('add_deserializer', add_deserializer)
    config.add_request_method(utility.deserialize_request_body,
                              'deserialized_body', reify=True)
    config.scan(__name__)


@implementer(IDeserializer)
class Utility(object):

    def __init__(self):
        self.accept_headers = MultiDict()
        self.deserializers = {}

    def add_deserializer(self, content_type, callable):
        self.deserializers[content_type] = callable
        self.accept_headers.add('Accept', content_type)

    def deserialize_request_body(self, request):
        content_type = request.content_type
        deserialized = None
        request.response.headers.extend(self.accept_headers)

        if content_type in self.deserializers:
            try:
                deserialized = self.deserializers[content_type](request)
            except HTTPException as http_exc:
                http_exc.headers.extend(self.accept_headers)
                raise
        else:
            raise HTTPUnsupportedMediaType(content_type,
                                           headers=self.accept_headers)

        return deserialized


def add_deserializer(config, content_type, deserializer_func):

    def callback():
        utility = config.registry.getUtility(IDeserializer)
        utility.add_deserializer(content_type, deserializer_func)

    intr = config.introspectable(
        category_name='Request body deserializers',
        discriminator=content_type,
        title=content_type,
        type_name='',
    )
    intr['deserializer'] = deserializer_func

    config.action(content_type, callback, introspectables=(intr, ))


class deserializer_config(object):

    def __init__(self, content_type):
        self.content_type = content_type

    def __call__(self, callable):

        def callback(context, name, callable):
            config = context.config.with_package(info.module)
            config.add_deserializer(self.content_type, callable, **settings)

        info = venusian.attach(callable, callback)
        settings = {'_info': info.codeinfo}

        return callable


@deserializer_config('application/json')
def deserialize_json(request):
    fp = request.body_file_seekable
    fp.seek(0)
    try:
        return json.load(fp, encoding=request.charset, parse_float=Decimal)
    except (ValueError, UnicodeDecodeError):
        raise HTTPBadRequest('invalid json body')


@deserializer_config('application/x-www-form-urlencoded')
@deserializer_config('multipart/form-data')
def deserialiaze_form_urlencoded(request):
    if isinstance(request.POST, NoVars):
        raise HTTPBadRequest('invalid %s body' % request.content_type)
    return request.POST.mixed()
