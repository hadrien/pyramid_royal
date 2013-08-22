from royal.resource import Root, Collection, Resource, PaginatedResult


__all__ = ['Root', 'Collection', 'Resource', 'PaginatedResult']


def includeme(config):
    config.include('royal.renderer')
    config.include('royal.views')
    config.commit()
