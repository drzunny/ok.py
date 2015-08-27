# -*-coding:utf8-*-
from __future__ import print_function
import re
import os
import sys
import glob
import okpy
import argparse

G_PARSER = argparse.ArgumentParser(prog='okpy', description='Run okpy for testing')
G_PARSER.add_argument('target', help='test a package or python file', type=str)
G_PARSER.add_argument('-d', '--details', help='show errors and exception if test case is fail', action='store_true')
G_PARSER.add_argument('--love', help='who will love you ?', action='store_true')

G_OPTIONS = G_PARSER.parse_args()

# --------------------------------------------
#  Helper functions
# --------------------------------------------
def _hint(what):
    print('\n%s\n\n' % what)


def _is_a_path(op):
    if op == '.':
        return True, op
    r = re.compile('[/\\:]')
    if r.search(op):
        return True, op
    if not op.startswith('-'):
        return True, op
    return False, op.strip('-').replace('-', ' ').replace('_', ' ')


def _setup_tests(path):
    full_path = os.path.abspath(path)
    if os.path.isdir(path):
        sys.path.append(full_path)
        # glob all python file without __init__.py
        files = glob.glob(full_path + '/*.py')
        for f in files:
            module_name = os.path.splitext(os.path.basename(f))[0]
            if module_name != '__init__':
                __import__(module_name)
    else:
        sys.path.append(os.path.dirname(full_path))
        module_name = os.path.splitext(os.path.basename(full_path))[0]
        __import__(module_name)


# --------------------------------------------
#  Entrypoint
# --------------------------------------------
def okpy_main():
    """
Usage:
    okpy [options] file/directory

options:
    --details:  output detail traceback if error

anything else?
    try `okpy --help` or `okpy --love`

--------------------
Have a nice day  :-)"""
    if not G_OPTIONS.target:
        _hint('No input file or directory, are you kidding me? \n\n %s' % okpy_main.__doc__)
        sys.exit(1)

    if G_OPTIONS.love:
        _hint('No body love you :-P')
        sys.exit(1)

    _setup_tests(G_OPTIONS.target)
    # Only support the `details` options
    okpy.run(G_OPTIONS.details)
