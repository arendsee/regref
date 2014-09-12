#!/usr/bin/env python3


import argparse
import re
import sys
import collections

__version__ = '2.0'
__prog__ = 'regref'

def parser(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--version',
        help='Display version',
        action='version',
        version='%(prog)s {}'.format(__version__)
    )
    parser.add_argument(
        'map',
        metavar='MAP',
        type=argparse.FileType('r'),
        help='space delimited file containing columns of strings'
    )
    parser.add_argument(
        'pat',
        metavar='PAT',
        nargs="?",
        help="regex pattern, '${n}' references nth column from MAP"
    )
    parser.add_argument(
        'rep',
        metavar='REP',
        default=None,
        nargs="?",
        help="replacement pattern, '${n}' references nth column from MAP"
    )
    parser.add_argument(
        '--where',
        nargs=2,
        metavar='COND',
        help='ARG1: a regex with one capture. ARG2: column number for capture'
    )
    args = parser.parse_args(argv)

    if args.where:
        if len(args.where) < 2:
            sys.exit("--where must have at least two arguments (e.g. --where 'id=(\d+)' 3)")
        else:
            Anchor = collections.namedtuple('Anchor', ['capture', 'column'])
            try:
                args.where = Anchor(args.where[0], int(args.where[1]) - 1)
                if args.where.column < 0:
                    raise ValueError
            except ValueError:
                sys.exit('Second argument to --where must be an integer >= 1')

    return(args)


class Selector:
    def __init__(self, capture, column, mapfile):
        self.capture = re.compile(capture)
        self.column = column
        self.repmap = self._load_map(mapfile)

    def _load_map(self, mapfile):
        repmap = dict()
        for line in mapfile:
            row = line.split()
            try:
                if row[self.column] in repmap:
                    msg = 'Column {} of MAP is not a unique key'
                    sys.exit(msg.format(self.column))
                repmap[row[self.column]] = row
            except IndexError:
                msg = 'MAP must have at least {} columns ({} found)'
                sys.exit(msg.format(self.column, len(row)))
        return(repmap)

    def get_maprow(self, line):
        try:
            m = re.search(self.capture, line)
            rowid = m.group(1)
            row = self.repmap[rowid]
        except (KeyError, IndexError, AttributeError):
            row = None
        return(row)

class Regref:
    def __init__(self, args, data=sys.stdin):

        opt = 4*bool(args.where) + 2*bool(args.pat) + bool(args.rep)

        self.pat = args.pat
        self.rep = args.rep
        self.data = data

        if opt in (4, 6, 7):
            self.selector = Selector(args.where.capture, args.where.column, args.map)
        else:
            self.patmap = [s.split() for s in args.map]

        # delete O(mn)
        if opt == 2:
            self.gen = self.delete_mn

        # search and replace O(mn)
        elif opt == 3:
            self.gen = self.search_and_replace_mn

        # search O(m + n)
        elif opt == 4:
            self.gen = self.search_m_plus_n

        # delete O(m + n)
        elif opt == 6:
            self.gen = self.delete_m_plus_n

        # search and replace O(m + n)
        elif opt == 7:
            self.gen = self.search_and_replace_m_plus_n

        else:
            sys.exit('Invalid option combination')

    def _replace(self, base_pat, base_rep, row, line):
        pat = self._specify_regex(base_pat, row)
        rep = self._specify_regex(base_rep, row)
        try:
            out = re.sub(pat, rep, line)
        except re.error as e:
            sys.exit('Invalid regular expression: {}'.format(e))
        return(out)

    def _delete(self, base_pat, row, line):
        pat = self._specify_regex(base_pat, row)
        try:
            out = re.sub(pat, '', line)
        except re.error as e:
            sys.exit('Invalid regular expression: {}'.format(e))
        return(out)

    def _specify_regex(self, r, row):
        try:
            rout = re.sub('\$\{(\d+)\}', lambda m: row[int(m.groups(1)[0])], r)
        except IndexError:
            sys.exit('MAP lacks column requested column')
        except re.error:
            sys.exit("Invalid regular expression: '{}'".format(r))
        return(rout)

    def delete_mn(self):
        for line in self.data:
            for row in self.patmap:
                line = self._delete(self.pat, row, line)
            yield line

    def search_and_replace_mn(self):
        for line in self.data:
            for row in self.patmap:
                line = self._replace(self.pat, self.rep, row, line)
            yield line

    def search_m_plus_n(self):
        for line in self.data:
            if self.selector.get_maprow(line):
                yield line

    def delete_m_plus_n(self):
        for line in self.data:
            row = self.selector.get_maprow(line)
            if row:
                line = self._delete(self.pat, row, line)
            yield line

    def search_and_replace_m_plus_n(self):
        for line in self.data:
            row = self.selector.get_maprow(line)
            if row:
                line = self._replace(self.pat, self.rep, row, line)
            yield line


if __name__ == '__main__':
    args = parser()

    for line in Regref(args).gen():
        print(line, end='')
