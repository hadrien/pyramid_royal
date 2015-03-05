
def includeme(config):
    config.include('royal.ext.sqla')
    config.include('example.ext.sqla.model')
    config.include('example.ext.sqla.resources')
    config.scan()
