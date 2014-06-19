import logging

from pyramid.interfaces import IRootFactory
from zope.interface import implementer

from royal import exceptions
from royal.interfaces import IResourceConfigurator

log = logging.getLogger(__name__)


def includeme(config):
    utility = config.registry.queryUtility(IResourceConfigurator)

    if utility is None:
        utility = ResourceConfigurator()
        config.registry.registerUtility(utility, name=u'')
        config.add_directive('add_resource', utility.add_resource)


class ResourceDefinition(object):
    def __init__(self, resource_path, collection_cls, item_cls, parent,
                 name):
        self.resource_path = resource_path
        self.collection_cls = collection_cls
        self.item_cls = item_cls
        self.parent = parent
        self.name = name

    def __repr__(self):
        return '<ResourceDefinition(%s)>' % self.resource_path


@implementer(IResourceConfigurator)
class ResourceConfigurator(object):
    """Internal configurator of royal resources.
    """

    intr_category_name = 'Royal resources'

    def __init__(self):
        self.definitions = {}
        self._ainfo = None

    def add_resource(self, config, resource_path):
        try:
            parent, name = resource_path.rsplit('.', 1)
        except ValueError:
            # no separator in resource name: it is a root resource
            parent = None
            name = resource_path

        module_name = '%s.%s' % (config.package_name,
                                 resource_path.replace('.', '_'))

        module = config.maybe_dotted(module_name)

        collection_cls = getattr(module, 'Collection', None)
        item_cls = getattr(module, 'Item', None)

        if not any((collection_cls, item_cls)):
            raise exceptions.InvalidConfig('no collection or item class in %s',
                                           module)

        if collection_cls:
            collection_cls.children = {}

        if item_cls:
            item_cls.children = {}

        discriminator = ('royal', resource_path)

        intr = config.introspectable(
            category_name=self.intr_category_name,
            discriminator=discriminator,
            title=resource_path,
            type_name='Resource',
        )
        intr['collection_cls'] = collection_cls
        intr['item_cls'] = item_cls
        if parent:
            intr.relate(self.intr_category_name, ('royal', parent))
        else:
            intr.relate('root factories', None)

        definition = ResourceDefinition(resource_path, collection_cls,
                                        item_cls, parent, name)

        self.definitions[resource_path] = definition

        # Actions must be taken from top-level resource to leaf after
        # root_factory has been set at order=0
        # let's use order parameter:
        order = 1 + resource_path.count('.')
        # 'app.user.message' would be at order 3
        # 'app.user' at 2
        # 'app' at 1

        config.action(discriminator, self.register_resource,
                      args=(config, resource_path), order=order,
                      introspectables=(intr,))

    def register_resource(self, config, resource_path):
        definition = self.definitions[resource_path]
        # get resource definition of parent
        parent_def = (self.definitions[definition.parent]
                      if definition.parent
                      else config.registry.queryUtility(IRootFactory))

        # get resource parent class
        parent_cls = (parent_def.item_cls
                      if hasattr(parent_def, 'item_cls')
                      else parent_def)

        parent_cls.children[definition.name] = (definition.collection_cls
                                                if definition.collection_cls
                                                else definition.item_cls)

        if all((definition.collection_cls, definition.item_cls)):
            definition.collection_cls.item_cls = definition.item_cls

        log.debug('add resource=%s parent_def=%s parent_cls=%s',
                  resource_path, parent_def, parent_cls)
