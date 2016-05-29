__author__ = 'oleh'

import argparse
from filters import run_filters
from load_script import load_site, start_test


def create_parser():
    p = argparse.ArgumentParser()

    p.add_argument('-l', '--load', nargs=2,
                   metavar=('url', 'dest'),
                   help='Load url content to hard disk')
    p.add_argument('-r', '--run', nargs=1,
                   metavar='filepath',
                   help='Run program for single wav file')
    p.add_argument('-w', '--watch',
                   metavar='TRUE_OR_FALSE',
                   help='Watch graphics analyzing')
    p.add_argument('-t', '--test', nargs=1,
                   metavar='testingFolder',
                   help='Run program for directory')
    return p


if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args()

    watch = namespace.watch and namespace.watch.upper() == 'TRUE'

    if namespace.load:
        url = namespace.load[0]
        dest = namespace.load[1]
        load_site(url, dest)

    elif namespace.run:
        f = namespace.run[0]
        run_filters(f, watch=watch)

    elif namespace.test:
        folder = namespace.test[0]
        start_test(folder)

    else:
        print 'No mode set'