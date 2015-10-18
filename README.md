# ok.py

**OK.py** is a simple and rough test tool, not a powerful test framework like `nose` or `unittest`, but it's pretty and lightweight.

For me, **TEST** means that I input a data to a API, then check the output is whether as same as my expectation.

So I wrote **OK.py**. It can help me to test my code more easily and explicitly.

If you only care about whether the API(s) output as same as it could be, and do not concern about its environment(such as multi-thread, multi-process), **OK.py** is worth to try.

> PS1. **OK.py** will support output JSON result to file in future release
>
> PS2. `EXPECT` is not supported in **OK.py**. Since you want to test your code,  **DON'T FORGIVE ANY ERROR**. `ASSERT` is our good friend.

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

Thanks to Python's decorator, I can name my function as I like.


# requirement

**[colorama](https://pypi.python.org/pypi/colorama)** - pretty colorful printing support
