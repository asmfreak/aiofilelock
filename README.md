# aiofilelock
[![PyPI](https://img.shields.io/pypi/v/aiofilelock.svg)](https://pypi.python.org/pypi/aiofilelock) [![PyPI](https://img.shields.io/pypi/pyversions/aiofilelock.svg)](https://pypi.python.org/pypi/aiofilelock) [![PyPI](https://img.shields.io/pypi/l/aiofilelock.svg)](https://pypi.python.org/pypi/aiofilelock) [![Say Thanks!](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/ASMfreaK)

Mutable and immutable file lock for asyncio

There are two possible locks exclusive (mutable file) and shared (immutable file).

```python
from aiofilelock import AIOMutableFileLock
import asyncio

async def main():
    with open('your-file', 'r+') as f:
        async with AIOMutableFileLock(f):
            f.write('VERY IMPORTANT DATA')
    with open('your-file', 'r+') as f:
        async with AIOImmutableFileLock(f):
            print(f.read())

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```

There is also `timeout`, after which the lock will raise a `BlockingIOError`
and `granularity`, the parameter of roughness of lock trials, both are in float seconds.
Negative timeout acts like non-blocking lock, None — infinite waiting time.

```python
from aiofilelock import AIOMutableFileLock
import asyncio

async def main():
    try:
        with open('your-file', 'r+') as f:
            # raise exception after 3 seconds, try flock each 0.5 seconds.
            async with AIOMutableFileLock(f, timeout=3, granularity=0.5):
                f.write('VERY IMPORTANT DATA')
    except BlockingIOError:
        print("couldn't acquire lock in time")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```
