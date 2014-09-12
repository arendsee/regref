#!/usr/bin/env python3

import regref
import unittest
import sys
import collections
import io
import os

if not os.path.exists('test-data'):
    os.mkdir('test-data')

class TestSelector(unittest.TestCase):
    def setUp(self):
        pat = [
            '12 aa ba',
            '13 ab bb',
            '14 ac bc'
        ]
        self.sel = regref.Selector(capture='id=(\d+)', column=0, mapfile=pat)

    def test_default(self):
        self.assertEqual(self.sel.get_maprow('yeah id=13'), ['13', 'ab', 'bb'])

    def test_no_match(self):
        self.assertEqual(self.sel.get_maprow('yeah whatever'), None)
        self.assertEqual(self.sel.get_maprow('yeah 13'), None)

    def test_match_but_not_in_map(self):
        # Happily return None if the capture isn't in the MAP
        self.assertEqual(self.sel.get_maprow('yeah id=15'), None)

    def test_multiple_match_one_in_map(self):
        # If there are multiple matches but only one in MAP, take that one
        self.assertEqual(self.sel.get_maprow('yeah id=15 id=13'), ['13', 'ab', 'bb'])

    def test_ambiguous_result(self):
        # If there are multiple matches with representations in MAP, die
        self.assertRaises(SystemExit, self.sel.get_maprow, 'yeah id=13 id=14')

class TestRegref(unittest.TestCase):
    def setUp(self):
        self.pmap = [
            '12 aa ba',
            '13 ab bb',
            '14 ac bc'
        ]
        self.data = [
            'asaa id=12',
            'asdf id=14',
            't aa id=42',
        ]
        self.pfile = self._make_file(self.pmap, name='simple-map.txt')

    def _make_file(self, pmap, name):
        datfile = os.path.join(os.getcwd(), 'test-data', name)
        with open(datfile, 'w') as f:
            for line in pmap:
                print(line, file=f)
        return(datfile)

    def _get_results(self, argv, data):
        args = regref.parser(argv)
        reg = [c for c in regref.Regref(args, data).gen()]
        return(reg)

    def test_delete_mn(self):
        reg = self._get_results([self.pfile, 's${2}'], self.data)
        self.assertEqual(reg, ['a id=12', 'asdf id=14', 't aa id=42'])

    def test_search_and_replace_mn(self):
        reg = self._get_results([self.pfile, '${2}', '<${3}>'], self.data)
        self.assertEqual(reg, ['as<ba> id=12', 'asdf id=14', 't <ba> id=42'])

    def test_search(self):
        reg = self._get_results([self.pfile, '--where', 'id=(\d+)', '1'], self.data)
        self.assertEqual(reg, ['asaa id=12', 'asdf id=14'])

    def test_search_and_replace_m_plus_n(self):
        reg = self._get_results([self.pfile, '${1}', '<${3}>', '--where', 'id=(\d+)', '1'], self.data)
        self.assertEqual(reg, ['asaa id=<ba>', 'asdf id=<bc>', 't aa id=42'])

    def test_delete_m_plus_n(self):
        reg = self._get_results([self.pfile, ' id=${1}', '--where', 'id=(\d+)', '1'], self.data)
        self.assertEqual(reg, ['asaa', 'asdf', 't aa id=42'])


if __name__ == '__main__':
    unittest.main(warnings='ignore')
