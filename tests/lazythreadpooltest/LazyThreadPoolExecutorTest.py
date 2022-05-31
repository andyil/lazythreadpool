import unittest
import threading
import time
import random
import logging
import sys

logging.basicConfig(stream=sys.stdout)

from lazythreadpool.LazyThreadPoolExecutor import LazyThreadPoolExecutor


class AtomicCounter:

    def __init__(self):
        self.n = 0
        self.lock = threading.Lock()

    def inc(self):
        with self.lock:
            self.n += 1


def fail_f():
    print(1/0)



class TestStringMethods(unittest.TestCase):

    def test_50(self):
        counter = AtomicCounter()
        with LazyThreadPoolExecutor(max_workers=30) as ltp:
            for i in range(50):
                ltp.submit(counter.inc)

        self.assertEqual(counter.n, 50)




if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    unittest.main()