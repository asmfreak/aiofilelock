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
import os
import unittest
import asyncio
import tempfile
import json
import time
from aiofilelock import AIOMutableFileLock, AIOImmutableFileLock, BadFileError


class TestMLock(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.file = tempfile.NamedTemporaryFile(delete=False)

    def tearDown(self):
        self.loop.close()
        os.remove(self.file.name)

    def test_lock(self):
        async def test(fn):
            with open(fn, "r+") as f:
                async with AIOMutableFileLock(f):
                    r = json.load(f)
                    r['counter'] += 1
                    await asyncio.sleep(0.5)  # simulate complex task
                    f.seek(0)
                    f.write(json.dumps(r))
        with open(self.file.name, "w") as f:
            lock = AIOMutableFileLock(f)
            self.loop.run_until_complete(lock.acquire())
            f.write(json.dumps(dict(counter=0)))
            self.loop.run_until_complete(lock.close())
        ts = time.time()
        NPROCS = 5
        t = asyncio.wait([test(self.file.name) for i in range(NPROCS)])
        self.loop.run_until_complete(t)
        with open(self.file.name) as f:
            r = json.load(f)
            self.assertEqual(r['counter'], NPROCS)
        delta = time.time() - ts
        self.assertTrue(delta > float(NPROCS)/2)

    def test_immutable_lock(self):
        async def test(fn):
            with open(fn, "r") as f:
                async with AIOImmutableFileLock(f):
                    r = json.load(f)
                    await asyncio.sleep(0.5)
                    return r['counter']
        with open(self.file.name, "w") as f:
            lock = AIOMutableFileLock(f)
            self.loop.run_until_complete(lock.acquire())
            f.write(json.dumps(dict(counter=1)))
            self.loop.run_until_complete(lock.close())
        ts = time.time()
        NPROCS = 5
        t = asyncio.wait([test(self.file.name) for i in range(NPROCS)])
        self.loop.run_until_complete(t)
        delta = time.time() - ts
        self.assertTrue(delta < float(NPROCS)/2)
        self.assertTrue(delta > 0.5)
        with self.assertRaises(BadFileError), open(self.file.name,'r+') as f:
            AIOImmutableFileLock(f)


if __name__ == '__main__':
    unittest.main()
