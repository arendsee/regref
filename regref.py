#!/usr/bin/env python3

import argparse
import re
import sys

def parser(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--pattern-file',
        help='Space delimited file containing columns of regex patterns'
    )
    parser.add_argument(
        '-m', '--matcher',
        help='Matching pattern'
    )
    parser.add_argument(
        '-p', '--pattern',
        help='Regex pattern'
    )
    parser.add_argument(
        '-r', '--replacement',
        help='Replacement regex pattern'
    )
    parser.add_argument(
        '-a', '--write-all',
        help='Write all lines, even if they do not match the Matcher pattern',
        action='store_true',
        default=False
    )
    args = parser.parse_args(argv)
    return(args)

class Searcher:
    def __init__(self, args):
        self._pat = self._load_patterns(args)
        self._match = self._compile_pattern(args.matcher)
        self._ppat = args.pattern
        self._rpat = args.replacement

    def _load_patterns(self, args):
        with open(args.pattern_file, 'r') as f:
            pat = {c[0]:c[1:] for c in (r.split() for r in f.readlines())}
        return(pat)

    def _compile_pattern(self, pat):
        try:
            cpat = re.compile(pat)
        except:
            print('Invalid patter "%s"' % pat, file=sys.stderr)
            raise SystemExit
        return(cpat)

    def reformat(self, line):
        g = re.search(self._match, line)
        try:
            key = g.group(1)
            var = [key] + self._pat[g.group(1)]
        except:
            return(None)
        out = re.sub(self._ppat.format(*var),
                     self._rpat.format(*var),
                     line)
        return(out)



if __name__ == '__main__':
    args = parser()
    searcher = Searcher(args)
    for line in sys.stdin:
        line = line.strip()
        out = searcher.reformat(line)
        if out:
            print(out)
        elif args.write_all:
            print(line)
