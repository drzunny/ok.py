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
#   helpers
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

class _Logger(object):
    def __write(self, s, color, indent, bright):
        if indent > 0:
            sys.stdout.write(' ' * indent)
        if not color:
            sys.stdout.write(u'%s' % s)
        elif bright:
            sys.stdout.write(u'%s%s%s%s' % (colorama.Style.BRIGHT, color, s, colorama.Style.NORMAL))
        else:
            sys.stdout.write(u'%s%s' % (color, s))
        return self

    def ok(self, s=u'√', indent=0, bright=False):
        return self.__write(s, colorama.Fore.GREEN, indent, bright)

    def warn(self, s=u'！', indent=0, bright=False):
        return self.__write(s, colorama.Fore.YELLOW, indent, bright)

    def fail(self, s=u'×', indent=0, bright=False):
        return self.__write(s, colorama.Fore.RED, indent, bright)

    def info(self, s, indent=0, bright=False):
        return self.__write(s, colorama.Fore.CYAN, indent, bright)

    def bright(self, s, indent=0):
        return self.__write(s, colorama.Style.BRIGHT, indent, False)

    def say(self, s, indent=0):
        return self.__write(s, None, indent, False)

    def summary(self, success, npass=0, nfail=0, elasped=0):
        details = '  %sPass%s: %d   %sFail%s: %d   %sElasped%s: %d Secs\n\n'
        print('\n\n')
        if success:
            self.ok('  [ OK ]', bright=True)
        else:
            self.fail('  [FAIL]', bright=True)
        B = colorama.Style.BRIGHT
        reset = colorama.Style.NORMAL
        sys.stdout.write(details % (B, reset, npass, B, reset, nfail, B, reset, elasped))
        return self

    def flush(self):
        print()
        return self


g_logger = _Logger()


def _parse_assert_error(s):
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


def _parse_exception_error(src, s, e):
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

def _reason_dict(d, **keys):
    output, s = '(%s)', ''
    first = True
    for k, v in d.iteritems():
        if keys and (k not in keys or not keys[k]):
            continue
        if not first:
            s += ', '
        else:
            first = False
        s += '%s: %s' % (k, str(v))
    return output % s


# ----------------------------------------------
#   core
# ----------------------------------------------
class OKCore(object):
    def __init__(self):
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
                    g_logger.say('Test Cases - %s:\n\n' % src, indent=2)
                yield fn()
            print('\n' * 2)
        filename = None
        if self.benchmark:
            for fn in self.benchmark:
                src = fn.__src__
                if filename != src:
                    filename = src
                    g_logger.say('Benchmark - %s:\n\n' % src, indent=2)
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
    _core.register(__test_body)
    return fn


def benchmark(n=1, timeout=1000):
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
        _core.performance(__benchmark_body)
        return fn
    return __benchmark_wrap


def cleaner(fn):
    _core.cleaner = fn
    return fn

# ----------------------------------------------
#   test apis
# ----------------------------------------------
def catch(proc, *args, **kwargs):
    try:
        proc(*args, **kwargs)
    except Exception, e:
        return e.__class__


def run(allow_details=False):
    succ = True
    counter = FormDict(npass=0, nfail=0, elapsed=time.time())
    # show logo
    print(__logo__)
    # if initialize callback is defined
    if _core.ready:
        _core.ready()

    # startup test
    for case in _core.loop():
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
                    g_logger.flush().say(case.error['detail']).flush()
            elif 'exception' in case:
                g_logger.say(_reason_dict(case.exception, code=True, line=True), indent=2)
                if allow_details:
                    g_logger.flush().say(case.exception['detail']).flush()

        if 'cost' in case:
            g_logger.say('(n: %d, cost:%f, limit:%f)' % (case.retry, case.cost, case.timeout), indent=2)
        g_logger.flush()

    counter.elapsed = time.time() - counter.elapsed
    g_logger.summary(succ, counter.npass, counter.nfail, counter.elapsed)
    if _core.cleaner:
        _core.cleaner()

    return sys.exit(not succ)


# -------------------------------------------
#   Run as script
# -------------------------------------------

if __name__ == '__main__':
    import glob
    allow_details, dest = False, None
    nargs = len(sys.argv)
    if nargs == 2:
        path = sys.argv[1]
        if not os.path.exists(path):
            if path in ('-h', '--help', 'help'):
                print('Nobody help you  :-)')
            elif path == '--details':
                print('Where is your test file/directory?')
            else:
                print("No such a file or directory : %s" % path)
            sys.exit(1)
        dest = path
    elif nargs >= 3:
        op, path = sys.argv[1], sys.argv[2]
        if op == '--details':
            allow_details = True
        elif op in ('-h', '--help', 'help'):
            print('Nobody help you :-(')
            sys.exit(1)
        else:
            print('Unknow option: %s' % op)
            sys.exit(1)
        if not os.path.exists(path):
            print("No such a file or directory : %s" % path)
            sys.exit(1)
        else:
            dest = path

    # TODO: glob the destinations
    if os.path.isdir(dest):
        import_path = dest
        sys.path.append(os.path.abspath(import_path))
        test_files = glob.glob(dest + '/*.py')
        for tf in test_files:
            name = os.path.splitext(os.path.basename(tf))[0]
            if name == '__init__':
                continue
            __import__(name)
    else:
        import_path = os.path.dirname(dest)
        sys.path.append(os.path.abspath(import_path))
        test_name = os.path.splitext(os.path.basename(dest))[0]
        __import__(test_name)

    run(allow_details)
