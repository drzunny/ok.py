# ok.py

![are you ok](http://i0.hdslb.com/video/2f/2fc528fee5d0cbfb98b266bb7ec3a1ad.jpg)

> Image from Internet

`ok.py` is a simple and rough test tool, not a powerful test framework like `nose` or `unittest`, but it's pretty and lightweight.

# how to use

There is no `setUp` or `tearDown` function in your test case, `ok.py` defines test case(s) explicitly:

```python

import pyok

@pyok.test
def i_am_awesome():
  pyok.asset(1 != 0)
  pyok.asset_raise(fun('hello'), catch=(KeyError, ValueError))


```

Thanks for Python's decorator, no "**test**" in our function name now.

# requirement

**[colorama](https://pypi.python.org/pypi/colorama)** - pretty colorful printing support
