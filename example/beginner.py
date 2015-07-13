# -*- coding:utf8 -*-
import fixpath
import pyok


def outer_exception():
    return 1/0-3


@pyok.ready
def are_you_ready():
    pass


@pyok.cleaner
def i_am_cleaner():
    pass


@pyok.test
def check_it_out():
    assert 1 != 2

@pyok.test
def check_it_out2():
    assert (1 - 2) > 0

@pyok.test
def check_it_out3():
    a = outer_exception()

@pyok.benchmark(n=1000, timeout=1000)
def benchmark_is_ok():
    n = 0
    for x in xrange(100):
        n += x


@pyok.benchmark(n=1, timeout=1)
def benchmark_is_ok2():
    import time
    time.sleep(3)



if __name__ == '__main__':
    pyok.run()
