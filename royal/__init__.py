from royal.resource import Root, Collection, Item


__all__ = ['Root', 'Collection', 'Item']


def includeme(config):
    config.include('royal.renderer')
    config.include('royal.utility')
    config.include('royal.resource')
    config.include('royal.views')
    config.commit()
