# -*- coding: utf-8
"""List all royal resources.
"""

import argparse
import logging
import functools
from collections import OrderedDict

from pyramid.paster import bootstrap

from royal.directives import category

log = logging.getLogger(__name__)


def main():  # pragma no cover
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config_uri',
                        help='PasteDeploy config file to use.')
    args = parser.parse_args()

    env = bootstrap(args.config_uri)
    print get_pretty_resource_list(env['registry'])


def get_pretty_resource_list(registry):
    introspector = registry.introspector
    intr_seq = introspector.get_category(category)

    introspectables = sorted([d['introspectable'] for d in intr_seq],
                             cmp=lambda x, y: cmp(x.title, y.title))

    resources = OrderedDict()
    for intr in introspectables:
        if intr.title in resources:
            resource = resources[intr.title]
        else:
            resource = resources[intr.title] = {
                'name': intr['name'],
                'pattern': '/' + intr.title.replace('.', '/(id)/'),
                'collection': None,
                'item': None,
            }

        resource[intr.type_name.lower()] = intr['dotted_name']

    return format(resources)


def format(resources):
    max_path_len = len(max(resources.keys(), key=len))
    max_pattern_len = len(max([r['pattern'] for k, r in resources.items()],
                              key=len))
    max_collection_len = len(max([r['collection']
                                  for k, r in resources.items()
                                  if r['collection']],
                                 key=len))
    max_item_len = len(max([r['item'] for k, r in resources.items()
                            if r['item']],
                           key=len))

    get_line = functools.partial(get_formatted_line,
                                 max_path_len + 1,
                                 max_pattern_len + 1,
                                 max_collection_len + 1,
                                 max_item_len + 1)

    header = get_line('Resource', 'Pattern', 'Collection', 'Item')

    underline = get_line('=' * (max_path_len + 1),
                         '=' * (max_pattern_len + 1),
                         '=' * (max_collection_len + 1),
                         '=' * (max_item_len + 1))
    body = ''
    for path, info in resources.items():
        body += get_line(path, info['pattern'], info['collection'],
                         info['item'])

    return header + underline + body


def get_formatted_line(column1_len, column2_len, column3_len, column4_len,
                       column1, column2, column3, column4):
    fmt = '{column1:{fill}{align}{column1_len}}'
    fmt += '{column2:{fill}{align}{column2_len}}'
    fmt += '{column3:{fill}{align}{column3_len}}'
    fmt += '{column4:{align}}\n'
    if column3 is None:
        column3 = ''
    if column4 is None:
        column4 = ''
    params = dict(column1=column1, column2=column2, column3=column3,
                  column4=column4, fill=' ', align='<',
                  column1_len=column1_len + 1,
                  column2_len=column2_len + 1,
                  column3_len=column3_len + 1,
                  column4_len=column4_len + 1)
    return fmt.format(**params)
