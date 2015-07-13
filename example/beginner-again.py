# -*- coding:utf8 -*-
import fixpath
import pyok

@pyok.test
def i_am_ok():
    assert 1 + 1 == 2


@pyok.benchmark(n=100, timeout=10000)
def i_am_lighting():
    s = 1 + 1


if __name__ == '__main__':
    pyok.run(True)
