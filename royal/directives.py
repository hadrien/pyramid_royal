import logging

from pyramid.interfaces import IRootFactory

from royal import exceptions

log = logging.getLogger(__name__)


def includeme(config):
    config.add_directive('add_resource', add_resource)
    config.add_directive('add_collection', add_collection)
    config.add_directive('add_item', add_item)


category = 'Royal resources'


def add_resource(config, resource_path):
    module_name = '%s.%s' % (config.package_name,
                             resource_path.replace('.', '_'))

    module = config.maybe_dotted(module_name)

    collection_cls = getattr(module, 'Collection', None)
    item_cls = getattr(module, 'Item', None)

    if not any((collection_cls, item_cls)):
        raise exceptions.InvalidConfig('no collection or item class in %s',
                                       module)

    _save_resource_definition(config, resource_path, collection_cls, item_cls)


def add_collection(config, resource_path, cls):
    _save_resource_definition(config, resource_path, cls, None)


def add_item(config, resource_path, cls):
    _save_resource_definition(config, resource_path, None, cls)


def _is_collection(introspectable):
    return introspectable.type_name == 'Collection'


def _is_item(introspectable):
    return introspectable.type_name == 'Item'


def _save_resource_definition(config, resource_path, collection_cls,
                              item_cls):
    try:
        _, name = resource_path.rsplit('.', 1)
    except ValueError:
        # no separator in resource name: it is a root resource
        name = resource_path

    if collection_cls:
        _new_action(config, resource_path, name, collection_cls, 'Collection')

    if item_cls:
        _new_action(config, resource_path, name, item_cls, 'Item')


def _new_action(config, resource_path, name, cls, type_name):
    hierarchy = resource_path.replace('.', '.item.')
    if type_name == 'Item':
        hierarchy += '.item'

    intr = config.introspectable(
        category_name=category,
        discriminator=('royal', hierarchy),
        title=resource_path,
        type_name=type_name,
    )
    intr['name'] = name
    intr['resource_path'] = resource_path
    intr['cls'] = cls
    intr['dotted_name'] = '%s:%s' % (cls.__module__, cls.__name__)

    # Actions must be taken from top-level resource to leaf after
    # root_factory has been set at order=0
    # let's use order parameter:
    # 'app.user.message' collection & item are respectively at order 5 & 6
    # 'app.user' collection & item are respectively at order 3 & 4
    # 'app' collection & item are respectively at order 1 & 2

    order = 1 + (resource_path.count('.') * 2) + (1 if _is_item(intr) else 0)

    config.action(intr.discriminator, register,
                  args=(config, intr), order=order,
                  introspectables=(intr, ))


def register(config, intr):
    parent = find_parent_intr(config.introspector, intr)
    cls = intr['cls']
    name = intr['name']
    cls.children = {}

    if parent is None:
        # root resource: (/users, /bob)
        root_cls = config.registry.queryUtility(IRootFactory)
        intr.relate('root factories', None)
        root_cls.children[name] = cls
        return

    intr.relate(category, parent.discriminator)

    parent_cls = parent['cls']

    if _is_item(intr):
        if _is_item(parent):
            # it's like having /user/1/profile but why not
            parent_cls.children[name] = cls
        else:
            # /users/1, /users/1/photos/123
            parent_cls.item_cls = cls
    else:
        if _is_collection(parent):
            # it's like having /users/photos
            raise exceptions.InvalidConfig(
                'Collection class %s configured with a collection class as'
                ' parent: %s' % (cls, parent_cls)
                )
        # /users/1/photos
        parent_cls.children[name] = cls


def find_parent_intr(introspector, intr):
    hierarchy = intr.discriminator[1]
    try:
        parent_hierarchy, _ = hierarchy.rsplit('.', 1)
    except ValueError:
        return None
    return introspector.get(
        category,
        ('royal', parent_hierarchy),
        )
