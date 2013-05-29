from royal.resource import (
    Collection,
    PaginatedResult,
    Resource,
    Root,
    )

__all__ = [
    "Collection",
    "PaginatedResult",
    "Resource",
    "Root",
    ]


def includeme(config):
    config.include('royal.renderer')
    config.include('royal.views')
