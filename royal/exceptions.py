

class Base(Exception):
    """Base exception class for all royal exceptions."""


class InvalidConfig(Base):
    ""


class InternalError(Base):
    ""


class ResourceException(Base):

    def __init__(self, resource, *args):
        """
        :param resource: Resource the exception is related with.
        """
        super(Base, self).__init__(resource, *args)

    @property
    def resource(self):
        return self.args[0]


class Conflict(ResourceException):
    """Raised in case of conflict, i.e.: Duplicated resource."""


class NotFound(ResourceException):
    pass


class MethodNotAllowed(ResourceException):
    def __init__(self, resource, http_method):
        super(MethodNotAllowed, self).__init__(resource, http_method)

    @property
    def http_method(self):
        return self.args[1]


class BadParameter(ResourceException):

    def __init__(self, resource, name, value, msg=''):
        """Raised when bad parameters are provided

        :param name: Parameter name
        :param value: Parameter value
        """
        super(BadParameter, self).__init__(resource, name, value, msg)

    @property
    def name(self):
        return self.args[1]

    @property
    def value(self):
        return self.args[2]
