# ok.py

![are you ok](http://static01.hket.com/res/v3/image/content/595000/597695/68318509gw1ernv3wtm2jj20g40a4jsh_1024.jpg)

> Image from Internet

**OK.py** is a simple and rough test tool, not a powerful test framework like `nose` or `unittest`, but it's pretty and lightweight.

I'm just a programmer, not a tester. For me, **TEST** means that I input a data to a API, then check the output is whether as same as my expectation.

So I wrote **OK.py**.

If you only care about whether the API(s) output as same as it could be, and do not concern about its environment(such as multi-thread, multi-process), **OK.py** is worth to try.

> **OK.py** will support output JSON result to file in future release

> `EXPECT` is not supported in **OK.py**. Since you want to test your code,  **DON'T FORGIVE ANY ERROR**. `ASSERT` is our good friend.

# how to use

There is no `setUp` or `tearDown` function in your test case, **OK.py** defines test case(s) explicitly:

```python
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
            run outer_exception (this is a __doc__)
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

```

Thanks for Python's decorator, no "**test**" in our function name now.


# requirement

**[colorama](https://pypi.python.org/pypi/colorama)** - pretty colorful printing support
