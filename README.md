# ok.py

![are you ok](http://static01.hket.com/res/v3/image/content/595000/597695/68318509gw1ernv3wtm2jj20g40a4jsh_1024.jpg)

> Image from Internet

`ok.py` is a simple and rough test tool, not a powerful test framework like `nose` or `unittest`, but it's pretty and lightweight.

# how to use

There is no `setUp` or `tearDown` function in your test case, `ok.py` defines test case(s) explicitly:

```python

import pyok

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
    assert 1 - 2 > 0

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



```

Thanks for Python's decorator, no "**test**" in our function name now.

# requirement

**[colorama](https://pypi.python.org/pypi/colorama)** - pretty colorful printing support
