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
