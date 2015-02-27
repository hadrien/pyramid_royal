from pyramid.config import Configurator


def main(global_config, **settings):  # pragma no cover
    config = Configurator(settings=settings)
    config.include(includeme)
    return config.make_wsgi_app()


def includeme(config):
    config.include('royal')
    config.include('royal.ext.sqla')
    config.include('example.ext.model')
    config.include('example.ext.resources')
    config.scan()
