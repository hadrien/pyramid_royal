from zope.interface import Attribute, Interface


class IBase(Interface):
    "Base for all context class."
    __name__ = Attribute('The __name__ attribute should be the name with '
                         'which a resource\'s parent refers to the resource '
                         'via __getitem__.')
    __parent__ = Attribute('Should be a reference to the resource\'s parent '
                           'resource instance in the tree')


class IRoot(IBase):
    "Root factory"
    request = Attribute('The request object.')
    links = Attribute('A mapping which gives relationship with other '
                      'resources.')


class IItem(IBase):

    def show(params):
        "GET /items/{id}"

    def update(params):
        "PUT /items/{id}"

    def patch(params):
        "PATCH /items/{id}"

    def delete():
        "DELETE /items/{id}"


class ICollection(IBase):

    def index(offset, limit, params):
        "GET /items?offset=0&limit=20"

    def create(params):
        "POST /items"

    def delete():
        "DELETE /items"


class IResourceConfigurator(Interface):

    def add_resource(dot_path):
        "Add a resource by its dot notation: 'apps.users' is apps/{id}/users"


class IDeserializer(Interface):

    def add_deserializer(content_type, callable):
        "Add a deserializer callable for a content type"

    def deserialize_request_body(request):
        "Deserialize request body according to its content type."


class IAdaptableRenderer(Interface):

    def add_adapter(type_or_iface, adapter):
        """ When an object of the type (or interface) ``type_or_iface`` fails
        to automatically encode using the serializer, the renderer will use
        the adapter ``adapter`` to convert it into a serializable object."""

    def __call__(info):
        """ Returns the encoded string with the content-type as the renderer
        defined (``application/json`` for a json renderer)."""
