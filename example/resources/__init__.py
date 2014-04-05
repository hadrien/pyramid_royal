

def includeme(config):
    from .root import Root
    config.set_root_factory(Root)

    config.add_resource('users')
    config.add_resource('users.photos')
    config.add_resource('photos')
    config.scan(__name__)
