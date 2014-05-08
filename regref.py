#!/usr/bin/env python3

import argparse
import re
import sys

__version__ = '1.1'
__prog__ = 'regref'

def parser(argv=None):
    parser = argparse.ArgumentParser(
        prog = __prog__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog = \
        '''
        Example:
        $ cat pat.tab
         asdf 1234
         qwer 2345
         gfhj 7890
        $ cat in.tab
         file1 ID=asdf
         file2 ID=qwer
         file3 ID=gfhj
         file4 ID=rrrr
        $ cat in.tab | regref -f pat.tab -m 'ID=(\S+)' -p 'ID=(\S+)' -r 'ID={1}'
         file1 ID=1234
         file2 ID=2345
         file3 ID=7890
        '''
    )
    parser.add_argument(
        '--version',
        help='Display version',
        action='version',
        version='%(prog)s {}'.format(__version__)
    )
    parser.add_argument(
        '-f', '--pattern-file',
        metavar='file',
        help='Space delimited file containing columns of regex patterns'
    )
    parser.add_argument(
        '-m', '--matcher',
        metavar='str',
        help='Matching pattern'
    )
    parser.add_argument(
        '-p', '--pattern',
        metavar='str',
        help='Regex pattern'
    )
    parser.add_argument(
        '-r', '--replacement',
        metavar='str',
        help='Replacement regex pattern'
    )
    parser.add_argument(
        '-a', '--write-all',
        help='Write all lines, even if they do not match',
        action='store_true',
        default=False
    )
    parser.add_argument(
        '-v', '--invert',
        help='Return only non-matching (does nothing if -m and -p)',
        action='store_true',
        default=False
    )
    args = parser.parse_args(argv)
    return(args)

class Reg:
    def __init__(self, args):
        self._pat = self._load_patterns(args)
        self._match = self._compile_pattern(args.matcher)
        self._ppat = args.pattern
        self._rpat = args.replacement

    def _load_patterns(self, args):
        raise NotImplemented

    def _compile_pattern(self, pat):
        try:
            cpat = re.compile(pat)
        except:
            print('Invalid patter "%s"' % pat, file=sys.stderr)
            raise SystemExit
        return(cpat)

    def _get_key(self, line):
        try:
            return(re.search(self._match, line).group(1))
        except:
            return(None)

    def read(self, line):
        raise NotImplemented

class Formatter(Reg):
    def _load_patterns(self, args):
        with open(args.pattern_file, 'r') as f:
            pat = {c[0]:c[1:] for c in (r.split() for r in f.readlines())}
        return(pat)

    def read(self, line):
        key = self._get_key(line)
        try:
            var = [key] + self._pat[key]
        except:
            return(None)
        out = re.sub(self._ppat.format(*var),
                     self._rpat.format(*var),
                     line)
        return(out)

class Searcher(Reg):
    def _load_patterns(self, args):
        with open(args.pattern_file, 'r') as f:
            pat = {c.strip() for c in f.readlines()}
        return(pat)

    def read(self, line):
        key = self._get_key(line)
        return(key in self._pat)

if __name__ == '__main__':
    args = parser()
    if(args.pattern and args.replacement):
        reformatter = Formatter(args)
        for line in sys.stdin:
            line = line.strip()
            out = reformatter.read(line)
            if out:
                print(out)
            elif args.write_all:
                print(line)
    else:
        searcher = Searcher(args)
        for line in sys.stdin:
            line = line.strip()
            matched = searcher.read(line)
            if (matched and not args.invert) or (not matched and args.invert):
                print(line)
