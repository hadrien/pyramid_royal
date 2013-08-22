# -*- coding: utf-8 -*-
from zope.interface import (
    Attribute,
    Interface,
    )


class IBase(Interface):
    __name__ = Attribute('The __name__ attribute should be the name with which'
                         'a resource’s parent refers to the resource via'
                         '__getitem__.')
    __parent__ = Attribute('Should be a reference to the resource’s parent'
                           'resource instance in the tree')


class IRoot(IBase):
    request = Attribute('The request object.')


class IResource(IBase):

    resource_name = Attribute('Resource name')
    links = Attribute('A mapping which gives relationship with other '
                      'resources.')

    def show():
        "GET /items/{id}"

    def put():
        "PUT /items/{id}"

    def patch():
        "PATCH /items/{id}"

    def delete():
        "DELETE /items/{id}"


class ICollection(IBase):

    def index(offset, limit, *args, **kwargs):
        "GET /items?offset=0&limit=20"

    def create(params):
        "POST /items"

    def delete():
        "DELETE /items"


class IPaginatedResult(Interface):
    total = Attribute('total of items or None')

    def __iter__(self):
        ""
