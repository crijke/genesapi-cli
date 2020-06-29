import argparse
import logging
import sys

from importlib import import_module


COMMANDS = {
    'fetch': {
        'args': ({
            'flag': 'storage',
            'help': 'Directory where to store cube data'
        }, {
            'flag': '--new',
            'help': 'Initialize Storage if it doesn\'t exist and start downloading',
            'action': 'store_true'
        }, {
            'flag': '--prefix',
            'help': 'Prefix of cube names to restrict downloading, e.g. "111"'
        }, {
            'flag': '--cronjob',
            'help': 'Indicate that this execution is run as a cronjob (for logging behaviour)',
            'action': 'store_true'
        }, {
            'flag': '--force-update',
            'help': 'Re-download all cubes regardless if they are already up to date.',
            'action': 'store_true'
        })
    },
    'build_schema': {
        'args': ({
            'flag': 'directory',
            'help': 'Directory with raw cubes downloaded via the `fetch` command'
        },)
    },
    'build_inventory': {
        'args': ({
                     'flag': 'directory',
                     'help': 'Directory with raw cubes downloaded via the `fetch` command'
                 },)
    },
    'build_markdown': {
        'args': ({
            'flag': 'schema',
            'help': 'JSON file from `build_schema` output'
        }, {
            'flag': 'output',
            'help': 'Output directory.'
        })
    },
    'build_regions': {
        'args': ({
            'flag': 'storage',
            'help': 'Directory with raw cubes downloaded via the `fetch` command'
        }, {
            'flag': '--host',
            'help': 'Elastic host:port to obtain stats from'
        }, {
            'flag': '--index',
            'help': 'Elastic index'
        })
    },
    'build_es_template': {
        'args': ({
            'flag': 'schema',
            'help': 'JSON file from `build_schema` output'
        }, {
            'flag': '--index-pattern',
            'help': 'Elasticsearch index pattern',
            'default': 'genesapi-*'
        }, {
            'flag': '--shards',
            'help': 'Number of shards for elasticsearch index',
            'type': int,
            'default': 5
        }, {
            'flag': '--replicas',
            'help': 'Number of replicas for elasticsearch index',
            'type': int,
            'default': 0
        })
    },
    'jsonify': {
        'args': ({
            'flag': 'storage',
            'help': 'Directory with raw cubes downloaded via the `fetch` command'
        }, {
            'flag': '--output',
            'help': 'Output directory. If none, print each record per line to stdout'
        }, {
            'flag': '--pretty',
            'help': 'Print pretty indented json (for debugging purposes)',
            'action': 'store_true'
        }, {
            'flag': '--cronjob',
            'help': 'Indicate that this execution is run as a cronjob (for logging behaviour)',
            'action': 'store_true'
        }, {
            'flag': '--prefix',
            'help': 'Prefix for cube names to filter for'
        }, {
            'flag': '--force-export',
            'help': 'Serialize cubes even if they are up to date according to the storage.',
            'action': 'store_true'
        }, {
            'flag': '--fulltext',
            'help': 'Index schema and region names and context for fulltext search',
            'action': 'store_true'
        })
    },
    'status': {
        'args': ({
            'flag': 'storage',
            'help': 'Directory to storage'
        }, {
            'flag': '--host',
            'help': 'Elastic host:port to obtain stats from'
        }, {
            'flag': '--index',
            'help': 'Elastic index'
        })
    }
}


def main():
    parser = argparse.ArgumentParser(prog='genesapi')
    parser.add_argument('--loglevel', default='INFO')
    subparsers = parser.add_subparsers(help='commands help')
    for name, opts in COMMANDS.items():
        subparser = subparsers.add_parser(name)
        subparser.set_defaults(func=name)
        for args in opts.get('args', []):
            flag = args.pop('flag')
            subparser.add_argument(flag, **args)

    args = parser.parse_args()
    logging.basicConfig(stream=sys.stderr, level=getattr(logging, args.loglevel))

    if hasattr(args, 'func'):
        try:
            func = import_module('genesapi.%s' % args.func)
            func.main(args)
        except ImportError:
            raise Exception('`%s` is not a valid command.' % args.func)
