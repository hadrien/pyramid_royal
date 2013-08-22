import logging
from functools import wraps

from onctuous import All, Coerce, InRange, Required, Schema

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
    config.scan('royal.views')


class BaseView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def wrap_dict(self, item, item_dict):
        result = {'links': dict((k, self.request.resource_url(v))
                                for k, v in item.links.iteritems())}
        if item_dict:
            result.update({item.resource_name: item_dict})
        return result

    def resource_url(self, *elements, **kw):
        return self.request.resource_url(self.context, *elements, **kw)


def get_params(request):
    try:
        return request.POST.mixed()
    except Exception:
        log.debug('Error parsing POST', exc_info=True)
        raise HTTPBadRequest('Error parsing request parameters')


@view_defaults(context=interfaces.ICollection, renderer='royal')
class CollectionView(BaseView):

    index_schema = {
        Required('offset', 0): All(Coerce(int), InRange(min=0)),
        Required('limit', 20): All(Coerce(int), InRange(min=1)),
        }

    def get_paginated_links(self, query, total_items):
        links = {}
        links['self'] = self.resource_url(query=query)
        offset = query['offset']
        limit = query['limit']

        query['offset'] = 0
        links['first'] = self.resource_url(query=query)

        offset_last_page = (total_items / limit - 1) * limit

        query['offset'] = max(0, offset_last_page)
        links['last'] = self.resource_url(query=query)

        has_previous = offset > 0
        if has_previous:
            query['offset'] = offset - 1
            links['previous'] = self.resource_url(query=query)

        has_next = total_items > offset + limit
        if has_next:
            query['offset'] = offset + 1
            links['next'] = self.resource_url(query=query)

        return links

    @view_config(request_method='GET', permission='index')
    def index(self):
        schema = Schema({})
        schema.schema.update(CollectionView.index_schema)
        if hasattr(self.context, 'index_schema'):
            schema.schema.update(self.context.index_schema.schema)

        query = schema(dict(self.request.GET.mixed()))
        result = self.context.index(**query)

        items = [self.wrap_dict(item, item.show()) for item in result]

        return {
            self.context.__name__: items,
            'links': self.get_paginated_links(result.query, result.total),
            }

    @view_config(request_method='POST', permission='create')
    def create(self):
        params = get_params(self.request)
        if hasattr(self.context, 'create_schema'):
            params = self.context.create_schema(params)

        item = self.context.create(**params)
        item_url = self.request.resource_url(item)
        self.request.response.headers['Location'] = item_url
        self.request.response.status_int = HTTPCreated.code
        return self.wrap_dict(item, item.show())


@view_defaults(context=interfaces.IResource, renderer='royal')
class ResourceView(BaseView):

    @view_config(request_method='GET', permission='show')
    @view_config(request_method='GET', permission='show',
                 context=interfaces.IRoot)
    def show(self):
        item = self.context.show()
        return self.wrap_dict(self.context, item)

    @view_config(request_method='PUT', permission='put')
    def put(self):
        params = get_params(self.request)
        item = self.context.put(**params)
        return self.wrap_dict(self.context, item)

    @view_config(request_method='PATCH', permission='patch')
    def patch(self):
        self.context.patch(get_params(self.request))
        return self.request.response

    @view_config(request_method='DELETE', permission='delete')
    def delete(self):
        self.context.delete()
        return self.request.response


@view_config(context=exc.MethodNotAllowed)
@view_config(context=interfaces.IBase)
def not_allowed(context, request):
    return HTTPMethodNotAllowed()


def log_error_dict(view_callable):
    @wraps(view_callable)
    def wrapper(context, request):
        result = view_callable(context, request)
        log.debug('%s: %s', type(context), result, exc_info=True)
        return result
    return wrapper


@view_config(context=exc.NotFound, renderer='royal', decorator=log_error_dict)
def item_not_found(context, request):
    request.response.status_int = HTTPNotFound.code
    return {
        'error': 'not_found',
        'resource': request.resource_url(context.resource)
        }


@view_config(context=exc.Conflict, renderer='royal', decorator=log_error_dict)
def conflict(context, request):
    request.response.status_int = HTTPConflict.code
    return {
        'error': 'already_exists',
        'resource': request.resource_url(context.resource)
        }


@view_config(context='onctuous.errors.Invalid',
             renderer='royal', decorator=log_error_dict)
def invalid_parameters(context, request):
    request.response.status_int = HTTPBadRequest.code
    return {
        'error': 'invalid_parameters',
        'message': unicode(context)
        }


@view_config(context=exc.BadParameter, renderer='royal',
             decorator=log_error_dict)
def bad_parameter(context, request):
    request.response.status_int = HTTPBadRequest.code
    return {
        'error': 'invalid_parameters',
        'message': '%s="%s"' % (context.name, context.value)
        }


@view_config(context=Exception, renderer='royal', decorator=log_error_dict)
def exception(context, request):
    request.response.status_int = HTTPInternalServerError.code
    return {
        'error': 'unexpected_error',
        'message': unicode(context),
        'error_class': type(context).__name__,
        }
