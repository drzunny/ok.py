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
  -----------------------------------
  ARE YOU OK ?
  -----------------------------------
'''

# ----------------------------------------------
#   Helper Data Structs
# ----------------------------------------------
class FormDict(dict):
    def __init__(self, **other):
        super(FormDict, self).__init__()
        if other:
            self.update(other)

    def __setattr__(self, name, val):
        if hasattr(super(FormDict, self), name):
            setattr(super(FormDict, self), name, val)
        else:
            self[name] = val

    def __getattr__(self, name):
        if hasattr(super(FormDict, self), name):
            return getattr(super(FormDict, self), name)
        else:
            return self[name] if name in self else None


# ----------------------------------------------
#  Exception Parsers
# ----------------------------------------------
class _ExceptionParser:
    @staticmethod
    def assert_error(s):
        error = {'detail': s}
        if not s:
            return ret
        infos = s.strip().split('\n')
        file_info, code = infos[-3], infos[-2]
        r = re.compile('File "([^"]+)", line (\d+), in (\w+)')
        match = r.findall(file_info)
        if match:
            filename, line, fn = match[0]
        else:
            return ret
        code = code.strip()
        error.update({'file': filename, 'line': int(line), 'function': fn, 'code': code})
        return error

    @staticmethod
    def exception_error(src, s, e):
        error = {'detail': s}
        s, r = s.strip(), re.compile('File "([^"]+)", line (\d+), in (\w+)')
        infos = s.split('\n')
        n, src = len(infos), os.path.abspath(src)

        # find the last error in test file
        for ln in xrange(n-3, -1, -2):
            text = infos[ln]
            match = r.findall(text)
            if not match:
                continue
            filename, line, fn = match[0]
            if os.path.relpath(filename) == os.path.relpath(src):
                code = infos[ln+1].strip()
                error.update({'file': filename, 'line': int(line), 'function': fn, 'code': code})
                break
        return error

    @staticmethod
    def reason_dict(d, **keys):
        output, s = '(%s)', ''
        first = True
        for k in keys:
            if k not in d or not keys[k]:
                continue
            s += '%s: %s, ' % (k, str(d[k]))
        return output % s[:-2]


# ----------------------------------------------
#  Pretty Printer
# ----------------------------------------------
class _PrettyPrinter:
    @staticmethod
    def logo():
        sys.stdout.write(__logo__)
        print()

    @staticmethod
    def title(t, filename):
        sys.stdout.write('\n  %s - %s\n' % (t, filename))
        print()

    @staticmethod
    def result(ok, desc, info=None, details=None):
        if ok:
            sys.stdout.write(u'      %s%s%s%s' % (colorama.Style.BRIGHT, colorama.Fore.GREEN, u'√', colorama.Style.NORMAL))
            sys.stdout.write(u'    %s%s%s' % (colorama.Style.BRIGHT, desc, colorama.Style.NORMAL))
        else:
            sys.stdout.write(u'      %s%s%s%s' % (colorama.Style.BRIGHT, colorama.Fore.RED, u'×', colorama.Style.NORMAL))
            sys.stdout.write(u'    %s  ' % desc)
            if info:
                sys.stdout.write(_ExceptionParser.reason_dict(info, code=True, line=True))
            if details:
                sys.stdout.write('\n\n%s\n' % details)
        print()

    @staticmethod
    def summary(success, npass=0, nfail=0, elasped=0):
        details = '  %sPass%s: %d   %sFail%s: %d   %sElasped%s: %d Secs\n\n'
        print('\n\n')
        B = colorama.Style.BRIGHT
        RESET = colorama.Style.NORMAL
        if success:
            sys.stdout.write('  %s%s[ OK ]%s' % (B, colorama.Fore.GREEN, RESET))
        else:
            sys.stdout.write('  %s%s[FAIL]%s' % (B, colorama.Fore.RED, RESET))
        sys.stdout.write(details % (B, RESET, npass, B, RESET, nfail, B, RESET, elasped))
        print()


# ----------------------------------------------
#   core
# ----------------------------------------------
class OKPyCore(object):
    """
        Core of ok.py
    """
    ready = None
    cleaner = None
    benchmark = []
    cases = []

    def register(cls, func):
        cls.cases.append(func)

    def performance(cls, func):
        cls.benchmark.append(func)

    def loop(cls):
        filename = None
        if self.cases:
            for fn in self.cases:
                src = fn.__src__
                if filename != src:
                    filename = src
                    g_logger.say('\n  Test Cases - %s:\n\n' % src)
                yield fn()
            print('\n' * 2)
        filename = None
        if cls.benchmark:
            for fn in cls.benchmark:
                src = fn.__src__
                if filename != src:
                    filename = src
                    g_logger.say('\n  Benchmark - %s:\n\n' % src)
                yield fn()


# ----------------------------------------------
#   Test Decorators
# ----------------------------------------------
def ready(fn):
    """
            register the function as a `ready` function
    """
    OKPyCore.ready = fn
    return fn


def test(fn):
    """
            Define a test case
    """
    def __test_body():
        doc = fn.__doc__.strip() if fn.__doc__ else ''
        ret = FormDict(ok=True, name=fn.__name__, desc=doc, src=inspect.getabsfile(fn))
        try:
            fn()
        except Exception, e:
            ret.ok = False
            s = cStringIO.StringIO()
            traceback.print_exc(file=s)
            if isinstance(e, AssertionError):
                ret.error = _parse_assert_error(s.getvalue())
            else:
                ret.exception = _parse_exception_error(ret.src, s.getvalue(), e)
            s.close()
        return ret
    __test_body.__src__ = inspect.getabsfile(fn)
    OKPyCore.register(__test_body)
    return fn


def benchmark(n=1, timeout=1000):
    """
        Define a benchmark

            n:          how many time you want to retry
            timeout:    timeout is timeout
    """
    def __benchmark_wrap(fn):
        def __benchmark_body():
            doc = fn.__doc__.strip() if fn.__doc__ else ''
            ret = FormDict(ok=True, name=fn.__name__, desc=doc, src=inspect.getabsfile(fn))
            ret.benchmark = {'retry': n, 'timeout': timeout, 'cost': 0}
            fn_src = inspect.getabsfile(fn)
            cost = 0
            try:
                t = time.time()
                for i in range(n):
                    fn()
                cost = time.time() - t
            except Exception, e:
                ret.ok = False
                s = cStringIO.StringIO()
                traceback.print_exc(file=s)
                ret.exception = _parse_exception_error(ret.src, s.getvalue(), e)
                s.close()
            else:
                ret.ok = cost <= timeout
                ret.benchmark['cost'] = cost
            return ret
        __benchmark_body.__src__ = inspect.getabsfile(fn)
        OKPyCore.performance(__benchmark_body)
        return fn
    return __benchmark_wrap


def cleaner(fn):
    """
        register a function as a cleaner function
    """
    OKPyCore.cleaner = fn
    return fn

# ----------------------------------------------
#   test apis
# ----------------------------------------------
def catch(proc, *args, **kwargs):
    """
        execute a function and try to catch and return its exception class
    """
    try:
        proc(*args, **kwargs)
    except Exception, e:
        return e.__class__


def run(allow_details=False):
    """
        start ok.py to test your code

            allow_details: enable traceback.print_exc after exception occured.
    """
    succ = True
    counter = FormDict(npass=0, nfail=0, elapsed=time.time())
    # show logo
    print(__logo__)
    # if initialize callback is defined
    if OKPyCore.ready:
        OKPyCore.ready()

    # startup test
    for case in OKPyCore.loop():
        display_name = case.name if not case.desc else case.desc
        if case.ok:
            counter.npass += 1
            g_logger.ok(indent=6, bright=True).bright(display_name, indent=4)
        else:
            succ = False
            counter.nfail += 1
            g_logger.fail(indent=6, bright=True).say(display_name, indent=4)
            if 'error' in case:
                g_logger.say(_reason_dict(case.error, code=True, line=True), indent=2)
                if allow_details:
                    g_logger.flush().warn('\n' + case.error['detail'] + '\n').flush()
            elif 'exception' in case:
                g_logger.say(_reason_dict(case.exception, code=True, line=True), indent=2)
                if allow_details:
                    g_logger.flush().warn('\n' + case.exception['detail'] + '\n').flush()

        if 'benchmark' in case and 'cost' in case.benchmark:
            g_logger.say('(n: %d, cost:%f, limit:%f)' % (case.benchmark['retry'], case.benchmark['cost'], case.benchmark['timeout']), indent=2)
        g_logger.flush()

    counter.elapsed = time.time() - counter.elapsed
    g_logger.summary(succ, counter.npass, counter.nfail, counter.elapsed)
    if OKPyCore.cleaner:
        OKPyCore.cleaner()

    return sys.exit(not succ)
