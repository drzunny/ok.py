# -*- coding:utf8 -*-
import fixpath
import pyok

G_ERROR_NUMBER = None

def outer_exception():
    return 1/0-3

def catcher_exception(n):
    return 1/(n-2)

@pyok.ready
def are_you_ready():
    global G_ERROR_NUMBER
    G_ERROR_NUMBER = 2


@pyok.cleaner
def i_am_cleaner():
    global G_ERROR_NUMBER
    G_ERROR_NUMBER = None


@pyok.test
def check_it_true():
    assert 1 != 2

@pyok.test
def check_it_wrong():
    assert (1 - 2) > 0

@pyok.test
def check_it_no_name_but_doc():
    """
            run outer_exception (this is a __doc__)
    """
    a = outer_exception()

@pyok.test
def check_it_catch():
    assert pyok.catch(catcher_exception, G_ERROR_NUMBER) in (ZeroDivisionError,)

@pyok.benchmark(n=1000, timeout=1000)
def benchmark_is_ok():
    n = 0
    for x in xrange(100):
        n += x


@pyok.benchmark(n=1, timeout=1)
def benchmark_is_fail():
    import time
    time.sleep(3)


if __name__ == '__main__':
    pyok.run()
