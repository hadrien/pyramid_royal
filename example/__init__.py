from pyramid.config import Configurator


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include('example.resources')
    return config.make_wsgi_app()
