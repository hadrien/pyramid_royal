

class ExceptionBase(Exception):

    @property
    def resource(self):
        return self.args[0]


class Conflict(ExceptionBase):
    pass


class NotFound(ExceptionBase):
    pass


class MethodNotAllowed(ExceptionBase):
    pass


class BadParameter(ExceptionBase):

    @property
    def name(self):
        return self.args[1]

    @property
    def value(self):
        return self.args[2]
