from pyramid.config import Configurator


def main(global_config, **settings):  # pragma no cover
    config = Configurator(settings=settings)
    config.include(includeme)
    return config.make_wsgi_app()


def includeme(config):
    config.include('royal')
    config.include('example.model')
    config.include('example.resources')
