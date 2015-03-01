import functools
import venusian


class _declarative_config(object):

    def __init__(self, directive_name, resource_path):
        self.resource_path = resource_path
        self.directive_name = directive_name

    def __call__(self, cls):

        def callback(context, name, cls):
            config = context.config.with_package(info.module)
            directive = getattr(config, self.directive_name)
            directive(self.resource_path, cls, **settings)

        info = venusian.attach(cls, callback)
        settings = {'_info': info.codeinfo}
        return cls


item_config = functools.partial(_declarative_config, 'add_item')
collection_config = functools.partial(_declarative_config, 'add_collection')
