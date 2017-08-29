"""
    aiofilelock - mutable and immutable file lock for asyncio

    Copyright 2017 Pavel Pletenev <cpp.create@gmail.com>
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import asyncio
from fcntl import lockf, flock, LOCK_EX, LOCK_SH, LOCK_NB, LOCK_UN
from typing import IO


class AIOMutableFileLock(object):
    """
    A lock for both read and write operations. This lock is excusive - no other process can
    acquire any kind of lock until it is unlocked.

    # Arguments

    file_ob : file object to lock

    # Example:
    It can be used both as an async context manager:
    ```python
    from aiofilelock import AIOMutableFileLock
    import asyncio
    async def main():
        with open('your-file', 'r+') as f:
            async with AIOMutableFileLock(f):
                f.write('VERY IMPORTANT DATA')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    ```
    And as object:
    ```python
    from aiofilelock import AIOMutableFileLock
    import asyncio
    async def main():
        f = open('your-file', 'r+')
        lock = AIOMutableFileLock(f)
        await lock.acquire()
        f.write('VERY IMPORTANT DATA')
        lock.close()
        f.close()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    ```
    """
    def __init__(self, file_ob: IO) -> None:
        self._file = file_ob

    def _acquire_lock(self):
        flock(self._file, LOCK_EX | LOCK_NB)

    def _unlock(self):
        flock(self._file, LOCK_UN)

    async def acquire(self):
        'grab the lock'
        while True:
            try:
                self._acquire_lock()
                return
            except BlockingIOError:
                await asyncio.sleep(1.0)

    async def __aenter__(self):
        await self.acquire()

    async def __aexit__(self, exc_type, exc, traceback):
        self._unlock()

    async def close(self):
        'release the lock'
        self._unlock()


class BadFileError(OSError):
    'Raised when AIOImmutableFileLock receives a not readonly file object'
    pass


class AIOImmutableFileLock(AIOMutableFileLock):
    """
    An immutable lock suited only for both read  operations.
    This lock is shared - any other process can also lock file with shared lock, but not with
    excusive lock. Thus the file can only be read not read.

    # Arguments

    file_ob : file object to lock

    # Example:
    It can be used both as an async context manager:
    ```python
    from aiofilelock import AIOImmutableFileLock
    import asyncio
    async def main():
        with open('your-file', 'r') as f:
            async with AIOImmutableFileLock(f):
                print(f.read())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    ```
    And as object:
    ```python
    from aiofilelock import AIOImmutableFileLock
    import asyncio
    async def main():
        f = open('your-file', 'r')
        lock = AIOImmutableFileLock(f)
        await lock.acquire()
        print(f.read())
        lock.close()
        f.close()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    ```
    """
    def __init__(self, file_ob: IO) -> None:
        if file_ob.mode != 'r':
            raise BadFileError('Cannot immutably lock a not readonly file')
        super().__init__(file_ob)

    def _acquire_lock(self):
        flock(self._file, LOCK_SH | LOCK_NB)
