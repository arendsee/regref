[![stable](http://badges.github.io/stability-badges/dist/stable.svg)](http://github.com/badges/stability-badges)
[![Build Status](https://travis-ci.org/arendsee/regref.svg?branch=master)](https://travis-ci.org/arendsee/regref)

# regref

## Installation

``` sh
pip3 install regref
```

You can access the CLI help messages with:

``` sh
regref -h
```

## Example

``` sh
./regref.py test-data/z.tab '${2}' '${3}' < test-data/z.fna
```

`z.fna` is a FASTA file with mangled headers where all non-letter or number
characters have been replaced with underscores.

`z.tab` is a table that contains the mangled names (in column 2) and the
original names (in column 3).

The `regref` command reads the FASTA file from standard input and then replaces
every occurrence of the mangled string with the original string.

The arguments '${2}' and '${3}' refer to columns in `z.tab` by column number.


`regref` will replace every occurrence of each pattern. The example below
replaces the mangled string in a tree with a single-quoted original string.

``` sh
./regref.py test-data/z.tab '${2}' "'\${3}'" < test-data/z.tre
```
