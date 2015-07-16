# -*-coding:utf8-*-
from __future__ import print_function
import re
import os
import sys
import glob
import okpy


def __hint(what):
    print('\n%s\n\n' % what)


def __is_a_path(op):
    if op == '.':
        return True, op
    r = re.compile('[/\\:]')
    if r.search(op):
        return True, op
    if not op.startswith('-'):
        return True, op
    return False, op.strip('-').replace('-', ' ').replace('_', ' ')


def __command_reader(args):
    ok, opts, dest = True, okpy.FormDict(), args[-1]
    nargs = len(args)
    if nargs > 1:
        op, dest = args[0], args[1]
        if op == '--details':
            opts.details = True
        else:
            is_path, op = __is_a_path(op)
            if is_path:
                opts.message = 'Invalid option: %s' % args[0]
                return False, opts, dest
            else:
                opts.message = 'No body %s you.   :-)' % op
                return False, opts, dest
    else:
        is_path, op = __is_a_path(args[0])
        if not is_path:
            opts.message = 'No body %s you.   :-(' % op
            return False, opts, dest

    if not os.path.exists(dest):
        opts.message = 'No such file or directory.  (%s)' % dest
        return False, opts, dest

    return ok, opts, dest


def __setup_tests(path):
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
    args = sys.argv
    if len(args) < 2:
        __hint('No input file or directory, are you kidding me? \n\n %s' % okpy_main.__doc__)
        sys.exit(1)

    ok, opts, dest = __command_reader(args[1:])
    if not ok:
        __hint(opts.message)
        sys.exit(1)

    __setup_tests(dest)
    # Only support the `details` options
    okpy.run(opts.details)
