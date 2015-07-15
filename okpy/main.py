# -*-coding:utf8-*-
from __future__ import print_function
import os
import sys
import glob
import okpy


def __hint(what):
    print('\n\n%s\n\n', what)


def __command_reader(args):
    ok, opts, dest = True, okpy.FormDict(), args[-1]
    nargs = len(args)
    if nargs > 1:
        op, dest = args[0], args[1]
        if op == '--details':
            opts.details = True
        else:
            op = op.strip('--')
            if op.find('/') >= 0 or op.find('\\') >= 0:
                opts.message = 'Invalid option: %s' % args[0]
                return False, opts, dest
            else:
                op = op.replace('-', ' ').replace('_', ' ')
                opts.message = 'No body %s you.   :-)' % op
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
    args = sys.argv
    if len(args) < 2:
        __hint('')
        sys.exit(1)

    ok, opts, dest = __command_reader(args[1:])
    if not ok:
        __hint(opts.message)
        sys.exit(1)

    __setup_tests(dest)
    # Only support the `details` options
    okpy.run(opt.details)
