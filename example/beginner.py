# -*- coding:utf8 -*-
import fixpath
import okpy

G_ERROR_NUMBER = None

def outer_exception():
    return 1/0-3

def catcher_exception(n):
    return 1/(n-2)

@okpy.ready
def are_you_ready():
    global G_ERROR_NUMBER
    G_ERROR_NUMBER = 2


@okpy.cleaner
def i_am_cleaner():
    global G_ERROR_NUMBER
    G_ERROR_NUMBER = None


@okpy.test
def check_it_true():
    assert 1 != 2

@okpy.test
def check_it_wrong():
    assert (1 - 2) > 0

@okpy.test
def check_it_no_name_but_doc():
    """
            this is a __doc__
    """
    a = outer_exception()

@okpy.test
def check_it_catch():
    assert okpy.catch(catcher_exception, G_ERROR_NUMBER) in (ZeroDivisionError,)

@okpy.benchmark(n=1000, timeout=1000)
def benchmark_is_ok():
    n = 0
    for x in xrange(100):
        n += x


@okpy.benchmark(n=1, timeout=1)
def benchmark_is_fail():
    import time
    time.sleep(3)


if __name__ == '__main__':
    okpy.run()
