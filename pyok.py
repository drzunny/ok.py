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
import cStringIO
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
    ret = {'pass': False, 'full': s}
    if not s:
        return ret
    infos = s.strip().split('\n')
    file_info, what = infos[-3], infos[-2]
    r = re.compile('File "([^"]+)", line (\d+), in (\w+)')
    match = r.findall(file_info)
    if match:
        filename, line, fn = match[0]
    else:
        return ret
    what = what.strip()
    ret.update({'pass': False, 'file': filename, 'line': int(line), 'function': fn, 'what': what})
    return ret

# ----------------------------------------------
#   core
# ----------------------------------------------
class OKCore(object):
    def __init__(self):
        self.filename = None
        self.ready = None
        self.cleaner = None
        self.benchmark = []
        self.cases = []

    def register(self, func):
        self.cases.append(func)

    def performance(self, func):
        self.benchmark.append(func)

    def loop(self):
        filename = None
        if self.cases:
            for fn in self.cases:
                src = fn.__src__
                if filename != src:
                    filename = src
                    g_logger.space(2).say('Test Cases - %s:\n\n' % src)
                yield fn()
            g_logger.space(2).say('\n\n\n')
        filename = None
        if self.benchmark:
            for fn in self.benchmark:
                src = fn.__src__
                if filename != src:
                    filename = src
                    g_logger.space(2).say('Benchmark - %s:\n\n' % src)
                yield fn()


_core = OKCore()

# ----------------------------------------------
#   decorators
# ----------------------------------------------
def ready(fn):
    _core.ready = fn
    return fn


def test(fn):
    def __test_body():
        err = {'pass': True, 'name': fn.__name__, 'desc': fn.__doc__}
        try:
            fn()
        except AssertionError, e:
            s = cStringIO.StringIO()
            traceback.print_exc(file=s)
            info = _parse_assert_error(s.getvalue())
            err.update(info)
            s.close()
        return err
    __test_body.__src__ = inspect.getabsfile(fn)
    _core.register(__test_body)
    return fn


def benchmark(n=1, timeout=1000):
    def __benchmark_wrap(fn):
        def __benchmark_body():
            ret = {'name': fn.__name__, 'desc': fn.__doc__}
            t = time.time()
            for i in range(n):
                fn()
            cost = time.time() - t
            ret.update({'cost': cost, 'pass': cost <= timeout, 'timeout': timeout, 'retry': n})
            return ret
        __benchmark_body.__src__ = inspect.getabsfile(fn)
        _core.performance(__benchmark_body)
        return fn
    return __benchmark_wrap


def cleaner(fn):
    _core.cleaner = fn
    return fn

# ----------------------------------------------
#   test apis
# ----------------------------------------------
def catch(proc):
    try:
        proc()
    except Exception, e:
        return e


def run():
    succ = True
    counter = {'pass': 0, 'fail': 0, 'elapsed': time.time()}
    # show logo
    _show_me_logo()
    # if initialize callback is defined
    if _core.ready:
        _core.ready()

    # startup test
    for case in _core.loop():
        if case['pass']:
            counter['pass'] += 1
            g_logger.space(8).ok().space(4).say(case['name'])
        else:
            succ = False
            counter['fail'] += 1
            g_logger.space(8).fail().space(4).say(case['name'])
            if 'what' in case:
                g_logger.space(4).say('(%s, line:%d)' % (case['what'], case['line']))

        if 'cost' in case:
            g_logger.space(4).say('(n: %d, cost:%f, limit:%f)' % (case['retry'], case['cost'], case['timeout']))
        g_logger.flush()

    counter['elapsed'] = time.time() - counter['elapsed']
    g_logger.summary(succ, counter['pass'], counter['fail'], counter['elapsed'])
    if _core.cleaner:
        _core.cleaner()

    return sys.exit(not succ)
