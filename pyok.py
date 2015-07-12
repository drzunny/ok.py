# -*- coding:utf8 -*-

# use print function
from __future__ import print_function

import re
import os
import sys
import time
import inspect
import platform
import colorama
import traceback

colorama.init(autoreset=True)

__logo__ = '''
  ARE YOU OK ?
  -----------------------------------
'''

# ----------------------------------------------
#   helpers
# ----------------------------------------------
class _Logger(object):
    def __init__(self):
        pass

    def space(self, n):
        sys.stdout.write(' ' * n)
        return self

    def ok(self, s=u'√'):
        sys.stdout.write(u'%s%s' % (colorama.Fore.GREEN, s))
        return self

    def warn(self, s=u'！'):
        sys.stdout.write(u'%s%s' % (colorama.Fore.YELLOW, s))
        return self

    def fail(self, s=u'×'):
        sys.stdout.write(u'%s%s' % (colorama.Fore.RED, s))
        return self

    def say(self, s):
        sys.stdout.write(s)
        return self

    def summary(self, success, npass=0, nfail=0, elasped=0):
        details = '  Pass: %s%d%s   Fail: %s%d%s   Elasped: %s%d%s Secs\n\n'
        print('\n\n')
        if success:
            self.ok('  [ OK ]')
        else:
            self.fail('  [FAIL]')
        yellow = colorama.Fore.YELLOW
        reset = colorama.Fore.RESET
        sys.stdout.write(details % (yellow, npass, reset, yellow, nfail, reset, yellow, elasped, reset))
        return self

    def flush(self):
        print()


g_logger = _Logger()


def _show_me_logo():
    print(__logo__)


def _parse_assert_error(s):
    if not s:
        return None
    _, file_info, what, _ = s.split('\n')
    r = re.compile('File "([^"]+)", line (\d+), in (\w+)')
    match = r.findall(file_info)
    if match:
        filename, line, fn = match[0]
    else:
        return None
    what = what.strip()
    return {'file': filename, 'line': line, 'function': fn, 'what': what}

# ----------------------------------------------
#   core
# ----------------------------------------------
class OKCore(object):
    def __init__(self):
        self.ready = None
        self.cleaner = None
        self.cases = {}
        self.result = []

    def register(self, name, func):
        src = inspect.getabsfile(func)
        name = '%s:%s' % (os.path.basename(src), name)
        self.cases[name +':test'] = func

    def loop(self):
        for rs in self.result:
            yield rs


_core = OKCore()

# ----------------------------------------------
#   decorators
# ----------------------------------------------
def ready(fn):
    _core.ready = fn
    return fn


def test(fn):
    _core.register(fn.__name__, fn)
    return fn


def benchmark(n=1, timeout=1000):
    def __benchmark_wrap(fn):
        def __benchmark_body():
            t = time.time()
            for i in range(n):
                fn()
            # TODO: add into result (timeover or not)
            return time.time() - t
        _core.register(fn.__name__, fn, type_name='benchmark')
        return __benchmark_body

    return __benchmark_wrap


def cleaner(fn):
    _core.cleaner = fn
    return fn

# ----------------------------------------------
#   test apis
# ----------------------------------------------
def expect(b):
    try:
        assert b
    except AssertionError, e:
        assert_error = None
        with cStringIO.StringIO() as s:
            traceback.print_exc(file=s)
            assert_error = _parse_assert_error(s.getvalue())
        if assert_error:
            # TODO: add into result
            pass


def assert_raise(proc, catch=None):
    pass


def run():
    succ = True
    counter = {'pass': 0, 'fail': 0, 'elapsed': 0}
    # show logo
    _show_me_logo()

    # if initialize callback is defined
    if _core.ready:
        _core.ready()

    # startup test
    for case in _core.loop():
        counter['elapsed'] += case.elapsed
        if case.ok:
            counter['pass'] += 1
            g_logger.space(8).ok().space(4).say(case.message)
        else:
            succ = False
            couter['fail'] += 1
            g_logger.space(8).fail().space(4).say(case.message)

    g_logger.summary(succ, counter['pass'], counter['fail'], counter['elapsed'])
    # if cleaner callback is defined
    if _core.cleaner:
        _core.cleaner()

    return sys.exit(not succ)
