# -*- coding:utf8 -*-
import fixpath
import pyok

@pyok.ready
def are_you_ready():
    pass


@pyok.cleaner
def i_am_cleaner():
    pass


@pyok.test
def check_it_out():
    pyok.expect(1 == 2)


if __name__ == '__main__':
    pyok.run()
