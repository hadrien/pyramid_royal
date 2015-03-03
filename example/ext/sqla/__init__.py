
def includeme(config):
    config.include('royal.ext.sqla')
    config.include('.model')
    config.include('.resources')
    config.scan()
