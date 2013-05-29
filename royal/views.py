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

from . import exceptions as exc
from . import resource

log = logging.getLogger(__name__)


def includeme(config):
    config.scan('royal.views')


class BaseView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def wrap_dict(self, item, item_dict):
        links = dict((k, self.request.resource_url(v))
                     for k, v in item.links.iteritems())
        return {'links': links, item.resource_name: item_dict}

    def resource_url(self, *elements, **kw):
        return self.request.resource_url(self.context, *elements, **kw)


def get_params(request):
    try:
        return request.POST
    except Exception:
        log.debug('Error parsing POST', exc_info=True)
        raise HTTPBadRequest('Error parsing request parameters')


@view_defaults(context=resource.Collection, renderer='royal')
class CollectionView(BaseView):

    index_schema = {
        Required('page', 0): All(Coerce(int), InRange(min=0)),
        Required('page_size', 20): All(Coerce(int), InRange(min=1)),
        }

    def get_paginated_links(self, query, total_items):
        links = {}
        links['self'] = self.resource_url(query=query)
        page = query['page']
        page_size = query['page_size']

        query['page'] = 0
        links['first'] = self.resource_url(query=query)

        query['page'] = max(0, total_items / page_size - 1)
        links['last'] = self.resource_url(query=query)

        has_previous = page > 0
        if has_previous:
            query['page'] = page - 1
            links['previous'] = self.resource_url(query=query)

        has_next = total_items > (page + 1) * page_size
        if has_next:
            query['page'] = page + 1
            links['next'] = self.resource_url(query=query)

        return links

    @view_config(request_method='GET')
    def index(self):
        schema = Schema({})
        schema.schema.update(CollectionView.index_schema)
        if hasattr(self.context, 'index_schema'):
            schema.schema.update(self.context.index_schema)

        query = schema(dict(self.request.GET))
        result = self.context.index(**query)

        items = [self.wrap_dict(item, item.model) for item in result]

        return {
            self.context.collection_name: items,
            'links': self.get_paginated_links(query, result.total),
            }

    @view_config(request_method='POST', permission='edit')
    def create(self):
        item = self.context.create(get_params(self.request))
        item_url = self.request.resource_url(item)
        self.request.response.headers['Location'] = item_url
        self.request.response.status_int = HTTPCreated.code
        return self.wrap_dict(item, item.model)


@view_defaults(context=resource.Resource, renderer='royal')
class ResourceView(BaseView):

    @view_config(request_method='GET', permission='show')
    def show(self):
        item = self.context.show()
        return self.wrap_dict(self.context, item)

    @view_config(request_method='PUT', permission='put')
    def put(self):
        item = self.context.put(get_params(self.request))
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
@view_config(context=resource.Collection)
@view_config(context=resource.Resource)
@view_config(context=resource.Root)
def not_allowed(context, request):
    return HTTPMethodNotAllowed()


def log_error_dict(view_callable):
    @wraps(view_callable)
    def wrapper(context, request):
        result = view_callable(context, request)
        log.debug('%s: %s', type(context), result)
        return result
    return wrapper


@view_config(context=exc.NotFound, renderer='royal')
@log_error_dict
def item_not_found(context, request):
    request.response.status_int = HTTPNotFound.code
    return {
        'error': 'not_found',
        'resource': request.resource_url(context.resource)
        }


@view_config(context=exc.Conflict, renderer='royal')
@log_error_dict
def conflict(context, request):
    request.response.status_int = HTTPConflict.code
    return {
        'error': 'already_exists',
        'resource': request.resource_url(context.resource)
        }


@view_config(context='onctuous.errors.Invalid',
             renderer='royal')
@log_error_dict
def invalid_parameters(context, request):
    request.response.status_int = HTTPBadRequest.code
    return {
        'error': 'invalid_parameters',
        'message': unicode(context)
        }


@view_config(context=exc.BadParameter, renderer='royal')
@log_error_dict
def bad_parameter(context, request):
    request.response.status_int = HTTPBadRequest.code
    return {
        'error': 'invalid_parameters',
        'message': '%s="%s"' % (context.name, context.value)
        }


@view_config(context=Exception, renderer='royal')
@log_error_dict
def exception(context, request):
    request.response.status_int = HTTPInternalServerError.code
    return {
        'error': 'unexpected_error',
        'message': unicode(context),
        'error_class': type(context).__name__,
        }
