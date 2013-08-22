# -*- coding: utf-8 -*-
from collections import OrderedDict
from datetime import datetime, date
from decimal import Decimal
import json
import logging

try:
    from bson import BSON
    from bson.objectid import ObjectId
except ImportError:
    pass

log = logging.getLogger(__name__)


def includeme(config):
    config.add_renderer('royal', Factory)


def json_dumps(o):
    return json.dumps(o, cls=JSONEncoder)


def json_loads(s):
    return json.loads(s, parse_float=Decimal)


def bson_dumps(o):
    return BSON.encode(o)


def bson_loads(s):
    return BSON(s).decode()


class Factory(object):
    """ Constructor: info will be an oect having the
    following attributes: name (the renderer name), package
    (the package that was 'current' at the time the
    renderer was registered), type (the renderer type
    name), registry (the current application registry) and
    settings (the deployment settings dictionary). """

    default_match = 'application/json'

    formatters = OrderedDict([
        ('application/json', json_dumps),
        ('application/bson', bson_dumps),
        ])

    def __init__(self, info):
        self.info = info

    def __call__(self, value, system):
        """ Call the renderer implementation with the value
        and the system value passed in as arguments and return
        the result (a string or unicode oect).  The value is
        the return value of a view.  The system value is a
        dictionary containing available system values
        # (e.g. view, context, and request). """
        request = system['request']
        format = request.accept.best_match(self.formatters.keys(),
                                           default_match=self.default_match)
        request.response.content_type = format
        return self.formatters[format](value)


class JSONEncoder(json.JSONEncoder):
    """Custom encoder that supports extra types.

    Supported types: date, datetime, Decimal, bson.objectid.ObjectId.
    """

    def default(self, o):
        if isinstance(o, (datetime, date)):
            return o.isoformat()

        if isinstance(o, Decimal):
            return _number_str(o)

        if isinstance(o, ObjectId):
            return str(o)

        return super(JSONEncoder, self).default(o)


class _number_str(float):
    # kludge to have decimals correctly output as JSON numbers;
    # converting them to strings would cause extra quotes

    def __init__(self, o):
        self.o = o

    def __repr__(self):
        return str(self.o)
