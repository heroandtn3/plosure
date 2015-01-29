#!/usr/bin/env python

# A simple Google Closure Compilers command line tool
# Author: Sang Hero
# Version 0.1.0
# License: GNU GPL v3

import requests
import argparse

import sys

API_URL = 'http://closure-compiler.appspot.com/compile'
COMPILATION_LEVEL = [
    'WHITESPACE_ONLY', 'SIMPLE_OPTIMIZATIONS', 'ADVANCED_OPTIMIZATIONS']
#API_URL = 'http://requestb.in/1jhhz8j1'

def js_compile(code, level='SIMPLE_OPTIMIZATIONS'):
    payload = {}

    # compilation level: 
    # WHITESPACE_ONLY, SIMPLE_OPTIMIZATIONS, ADVANCED_OPTIMIZATIONS
    payload['compilation_level'] = level

    # output format: json, xml, text
    payload['output_format'] = 'json'

    # output infor
    payload['output_info'] = [
        'compiled_code', 'warnings', 'errors', 'statistics']

    payload['warning_level'] = 'VERBOSE'
    payload['js_code'] = code

    r = requests.post(API_URL, data=payload)
    return r.json()

def format_size(size):
    """Convert a file size to human-readable form.
    Keyword arguments:
    size -- file size in bytes
    Returns: string.
    """
    SUFFIXES = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']
    if size < 0:
        raise ValueError('size must be non-negative')

    multiple = 1024
    for suffix in SUFFIXES:
        size /= multiple
        if size < multiple:
            return '%.2f %s' % (size, suffix)



def show_statistics(statistics):
    if not statistics:
        print('No statistics!')
    print('Original Size: %s gzipped (%s uncompressed)' % (
            format_size(statistics['originalGzipSize']),
            format_size(statistics['originalSize']),
        ))
    print('Compiled Size: %s gzipped (%s uncompressed)' % (
            format_size(statistics['compressedGzipSize']),
            format_size(statistics['compressedSize'])
        ))


def show_warning(warnings, show_full=False):
    if not warnings:
        print('No warnings!')
        return;

    print(len(warnings), 'warnings')
    if show_full:
        for warning in warnings:
            print('File:', warning['file'])
            print('\tType:', warning['type'])
            print('\tLine:', warning['lineno'])
            print('\tMessage:', warning['warning'])
            print('\tCode:', warning['line'])


def show_error(errors, show_full=False):
    if not errors:
        print('No errors!');
        return;

    print(len(errors), 'errors')


def write_output(output, filename):
    with open(filename, 'w') as f:
        f.write(output)


arg_parser = argparse.ArgumentParser(
    description='Google Closure Compilers command line tool')

arg_parser.add_argument(
    '-i', '--input', type=str, dest='js_inputs', required=True, nargs='+',
    help='JS files to be compressed')

arg_parser.add_argument(
    '-o', '--output', type=str, dest='js_output', required=True,
    help='Output compressed file')

arg_parser.add_argument(
    '-l', '--level', type=int, choices=[1, 2, 3], default=2,
    help='Compilation level, default is 2')

arg_parser.add_argument(
    '-v', '--verbose', action='store_true', help='Show all warings, errors')

args = arg_parser.parse_args()

print('Reading files...')
js_content = []
for js_input in args.js_inputs:
    with open(js_input, 'r') as f:
        js_content.append(f.read())

print('Sending request...')
output = js_compile(js_content, COMPILATION_LEVEL[args.level - 1])
print()
show_statistics(output.get('statistics'))
show_warning(output.get('warnings'), args.verbose)
show_error(output.get('errors'), args.verbose)
write_output(output.get('compiledCode'), args.js_output)