#!/usr/bin/env python3.6

"""
Simple template engine.

Usage:

    generate.py [options] foo.go.tpl

Example:

    generate.py --prefix=int --PREFIX=Int -DELEM=int32 --package=tests --output=unsafe.go ../unsafe.go.tpl

--prefix=arg replaces all occurrences of "zz" with "arg".

--PREFIX=Arg replaces all occurrences of "ZZ" with "Arg". If --Prefix is omitted,
  it defaults to --prefix, with its first letter uppercased.

--Dfrom=to replaces all occurrences of "from" with "to". This flag can be set multiple times.

--output=path specifies the output file name.

"""

import re
import argparse
import subprocess
import sys

def main() -> None:
    "Main application entry point"
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--package', default='funkymonkeypackage',
        help="Occurrences of 'PACKAGE' in the template are replaced with this string.")
    parser.add_argument(
        '--prefix', default='funkymonkey',
        help="Occurrences of 'zz'  in the template are replaced with this string")
    parser.add_argument(
        '--PREFIX', default='',
        help="Occurrences of 'ZZ'  in the template are replaced with this string")
    parser.add_argument(
        '-o', '--output', default='',
        help="Output destination. Defaults to standard output")
    parser.add_argument(
        '-D', '--define', default=[],
        type=str, action='append',
        help="str=replacement")
    parser.add_argument(
        'template', help="*.go.tpl file to process")

    opts = parser.parse_args()
    if not opts.PREFIX:
        if opts.prefix:
            opts.PREFIX = opts.prefix[0].upper() + opts.prefix[1:]

    defines = []
    for d in opts.define:
        m = re.match("^([^=]+)=(.*)", d)
        if m is None:
            raise Exception("Invalid -D option: " + d)
        defines.append((m[1], m[2]))

    out = sys.stdout
    if opts.output != '':
        out = open(opts.output, 'w')
    proc = subprocess.Popen(['goimports'], stdin=subprocess.PIPE, stdout=out, universal_newlines=True)

    print('// Code generated by \"', ' '.join(sys.argv), '\". DO NOT EDIT.\n', file=proc.stdin)

    for line in open(opts.template, 'r').readlines():
        line = line.replace('ZZ', opts.PREFIX)
        line = line.replace('zz', opts.prefix)
        line = line.replace('PACKAGE', opts.package)
        for def_from, def_to in defines:
            line = line.replace(def_from, def_to)
        print(line, end='', file=proc.stdin)
    proc.stdin.close()
    status = proc.wait()
    if status != 0:
        raise Exception('goimports failed: %s', status)
    if out != sys.stdout:
        out.close()

main()
