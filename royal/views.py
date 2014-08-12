import logging

from pyramid.settings import asbool
from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import (
    HTTPCreated,
    HTTPConflict,
    HTTPBadRequest,
    HTTPInternalServerError,
    HTTPNotFound,
    HTTPMethodNotAllowed,
)


from royal import exceptions as exc
from royal import interfaces

log = logging.getLogger(__name__)


def includeme(config):
    config.scan(__name__)
    in_debug_mode = asbool(config.registry.get('debug', True))
    if not in_debug_mode:
        config.add_view(exception, context=Exception, renderer='royal')


class BaseView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request


@view_defaults(context=interfaces.ICollection, renderer='royal')
class CollectionView(BaseView):

    @view_config(request_method='GET', permission='index')
    def index(self):
        func = self.context.index
        query_params = self.request.GET.mixed()
        if hasattr(self.context, 'index_schema'):
            result = func(self.context.index_schema(query_params))
        else:
            result = func(query_params)

        return result

    @view_config(request_method='POST', permission='create')
    def create(self):
        func = self.context.create

        params = self.request.deserialized_body
        if hasattr(self.context, 'create_schema'):
            params = self.context.create_schema(params)

        item = func(params)

        if hasattr(item, 'url'):
            self.request.response.headers['Location'] = item.url()
            self.request.response.status_int = HTTPCreated.code

        return item


@view_defaults(context=interfaces.IItem, renderer='royal')
class ItemView(BaseView):

    @view_config(request_method='GET', permission='show')
    @view_config(request_method='GET', permission='show',
                 context=interfaces.IRoot)
    def show(self):
        func = self.context.show
        params = self.request.GET.mixed()
        return func(params)

    @view_config(request_method='PUT', permission='replace')
    def put(self):
        func = self.context.replace
        params = self.request.deserialized_body
        return func(params)

    @view_config(request_method='PATCH', permission='update')
    def patch(self):
        func = self.context.update
        params = self.request.deserialized_body
        func(params)
        return self.request.response

    @view_config(request_method='POST')
    def post(self):
        # XXX should we permit POST on Item
        raise exc.MethodNotAllowed(self, 'POST')


@view_config(context=interfaces.IItem, request_method='DELETE',
             permission='delete', renderer='royal')
@view_config(context=interfaces.ICollection, request_method='DELETE',
             permission='delete', renderer='royal')
def delete(context, request):
    context.delete()
    return {}


@view_config(context=exc.MethodNotAllowed, renderer='royal')
@view_config(context=interfaces.ICollection, renderer='royal')
@view_config(context=interfaces.IItem, renderer='royal')
@view_config(context=interfaces.IRoot, renderer='royal')
def not_allowed(context, request):
    request.response.status_int = HTTPMethodNotAllowed.code
    return {
        'error': 'method_not_allowed',
        'resource': request.resource_url(context.resource
                                         if hasattr(context, 'resource')
                                         else context),
        'http_method': request.method
    }


@view_config(context=exc.NotFound, renderer='royal')
def item_not_found(context, request):
    request.response.status_int = HTTPNotFound.code
    return {
        'error': 'not_found',
        'resource': request.resource_url(context.resource)
    }


@view_config(context=exc.Conflict, renderer='royal')
def conflict(context, request):
    request.response.status_int = HTTPConflict.code
    return {
        'error': 'already_exists',
        'resource': request.resource_url(context.resource)
    }


@view_config(context=exc.BadParameter, renderer='royal')
def bad_parameter(context, request):
    request.response.status_int = HTTPBadRequest.code
    return {
        'error': 'invalid_parameters',
        'resource': request.resource_url(context.resource),
        'message': '%s="%s"' % (context.name, context.value),
    }


def exception(context, request):
    request.response.status_int = HTTPInternalServerError.code
    return {
        'error': 'unexpected_error',
        'message': unicode(context),
        'error_class': type(context).__name__,
    }
