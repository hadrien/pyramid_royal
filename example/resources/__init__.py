import royal

from . import singer


def includeme(config):
    config.set_root_factory(Root)


class Root(royal.Root):

    children = {
        'singers': singer.Collection,
        }

    def __getitem__(self, key):
        return self.children[key](key, self)
