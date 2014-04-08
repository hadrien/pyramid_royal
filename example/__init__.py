from bson import BSON
from pyramid.config import Configurator

from royal import deserializer_config


def main(global_config, **settings):  # pragma no cover
    config = Configurator(settings=settings)
    config.include(includeme)
    return config.make_wsgi_app()


def includeme(config):
    config.include('royal')
    config.include('example.model')
    config.include('example.resources')
    config.scan()


@deserializer_config('application/bson')
def deserialize_bson(request):
    return BSON(request.body.decode(request.charset)).decode()


@deserializer_config('multipart/form-data')
def deserialize_multipart_form_data(request):
    return request.POST.mixed()
