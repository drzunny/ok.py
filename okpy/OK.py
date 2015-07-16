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
import itertools
import cStringIO
import traceback

from colorama import Fore, Style

colorama.init(autoreset=True)

__logo__ = '''
  -----------------------------------
  ARE YOU OK ?
  -----------------------------------
'''

# ----------------------------------------------
#   Helper Data Structs and methods
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


def _case_groupby(cases):
    group_cases = {}
    for k, case in itertools.groupby(cases, lambda fn:fn.__src__):
        if k not in group_cases:
            group_cases[k] = list(case)
        else:
            group_cases[k] += list(case)
    return group_cases


# ----------------------------------------------
#  Exception Parsers
# ----------------------------------------------
class _ResultParser:
    @staticmethod
    def assert_error(s):
        error = {'details': s}
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
        error = {'details': s}
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
            if os.path.normcase(filename) == os.path.normcase(src):
                code = infos[ln+1].strip()
                error.update({'file': filename, 'line': int(line), 'function': fn, 'code': code})
                break
        return error

    @staticmethod
    def error_reason(d, allow_details=False):
        output = '(  line:%d | %s   )' % (d['line'], d['code'])
        output = '%s%s%s%s%s' % (Style.BRIGHT, Fore.YELLOW, output, Fore.RESET, Style.RESET_ALL)
        if allow_details:
            output += '\n\n%s%s%s%s%s\n' % (Style.BRIGHT, Fore.BLACK, d['details'], Fore.RESET, Style.RESET_ALL)
        return output


    @staticmethod
    def benchmark_reason(d):
        s = '(retry: %d, cost:%f, timeout: %f)' % (d['retry'], d['cost'], d['timeout'])
        if d['cost'] <= d['timeout']:
            return s
        else:
            return '%s%s%s%s%s' % (Style.BRIGHT, Fore.YELLOW, s, Fore.RESET, Style.RESET_ALL)


# ----------------------------------------------
#  Pretty Printer
# ----------------------------------------------
class _PrettyPrinter:
    @staticmethod
    def logo():
        """
            Print logo
        """
        sys.stdout.write(__logo__)
        print()

    @staticmethod
    def title(t, filename):
        """
            Print test cases title
        """
        sys.stdout.write('\n  %s - %s\n' % (t, filename))
        print()

    @staticmethod
    def result(cases, allow_details=False):
        """
            Print details result
        """
        cases_name = cases.desc if cases.desc else cases.name
        is_benchmark = 'benchmark' in cases
        if cases.ok:
            sys.stdout.write(u'      %s%s%s%s' % (Style.BRIGHT, Fore.GREEN, u'√', Style.NORMAL))
            sys.stdout.write(u'    %s%s%s    ' % (Style.BRIGHT, cases_name, Style.NORMAL))
            if allow_details and is_benchmark:
                sys.stdout.write(_ResultParser.benchmark_reason(cases.benchmark))
        else:
            sys.stdout.write(u'      %s%s%s%s' % (Style.BRIGHT, Fore.RED, u'×', Style.NORMAL))
            sys.stdout.write(u'    %s%s    ' % (Style.NORMAL, cases_name))

            # Print Exception > Print (benchmark fail | assert fail)
            trace_text = None
            if 'exception' in cases:
                sys.stdout.write(_ResultParser.error_reason(cases.exception, allow_details))
            elif is_benchmark:
                sys.stdout.write(_ResultParser.benchmark_reason(cases.benchmark))
            else:
                sys.stdout.write(_ResultParser.error_reason(cases.error, allow_details))

        # next line
        print()


    @staticmethod
    def summary(success, npass=0, nfail=0, elasped=0):
        """
            Print test summary
        """
        details = '  %sPass%s: %d   %sFail%s: %d   %sElasped%s: %d Secs\n\n'
        print('\n\n')
        B = Style.BRIGHT
        RESET = Style.NORMAL
        if success:
            sys.stdout.write('  %s%s[ OK ]%s' % (B, Fore.GREEN, RESET))
        else:
            sys.stdout.write('  %s%s[FAIL]%s' % (B, Fore.RED, RESET))
        sys.stdout.write(details % (B, RESET, npass, B, RESET, nfail, B, RESET, elasped))
        print()


# ----------------------------------------------
#   core
# ----------------------------------------------
class OKPyCore:
    """
        Core of ok.py
    """
    ready = None
    cleaner = None
    benchmark = []
    cases = []

    @classmethod
    def register(cls, func):
        cls.cases.append(func)

    @classmethod
    def performance(cls, func):
        cls.benchmark.append(func)

    @classmethod
    def loop(cls):
        """
            Execute the test cases and yield its results
        """
        cases_groups, benchmark_groups = _case_groupby(cls.cases), _case_groupby(cls.benchmark)
        # test cases
        for k, cases in cases_groups.iteritems():
            for fn in cases:
                yield 'DATA', k, fn()

        # have a break
        yield 'PAUSE', None, None

        # benchmakr start
        for k, cases in benchmark_groups.iteritems():
            for fn in cases:
                yield 'DATA', k , fn()

        yield 'END', None, None



# ----------------------------------------------
#   Test Decorators
# ----------------------------------------------
def ready(fn):
    """
            register the function as a `ready` function
    """
    OKPyCore.ready = staticmethod(fn)
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
                ret.error = _ResultParser.assert_error(s.getvalue())
            else:
                ret.exception = _ResultParser.exception_error(ret.src, s.getvalue(), e)
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
                ret.exception = _ResultParser.exception_error(ret.src, s.getvalue(), e)
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
    OKPyCore.cleaner = staticmethod(fn)
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
    _PrettyPrinter.logo()
    # if initialize callback is defined
    if OKPyCore.ready:
        OKPyCore.ready()

    # startup test
    mode = 'Test Cases'
    last_file = ''

    # Execute the test cases and read its results
    for status, filename, cases in OKPyCore.loop():
        if status == 'PAUSE':
            mode = 'Benchmark'
            last_file = ''
            continue
        elif status == 'END':
            break

        if last_file != filename:
            _PrettyPrinter.title(mode, filename)
            last_file = filename
        if cases.ok:
            counter.npass += 1
        else:
            counter.nfail += 1
            succ = False
        _PrettyPrinter.result(cases, allow_details=allow_details)

    # Output the summary result
    counter.elapsed = time.time() - counter.elapsed
    _PrettyPrinter.summary(succ, counter.npass, counter.nfail, counter.elapsed)
    if OKPyCore.cleaner:
        OKPyCore.cleaner()

    return sys.exit(not succ)