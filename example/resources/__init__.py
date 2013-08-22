

def includeme(config):
    from .root import Root
    config.set_root_factory(Root)
