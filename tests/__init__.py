import os
import re
import tempfile
import time
import threading
import unittest

from interruptingcow import timeout, StateException

class TestInterrupt(unittest.TestCase):

    def test_interrupt(self):
        with timeout(0.5):
            self.assertRaises(RuntimeError, time.sleep, 2)

    def test_regex(self):
        with timeout(.5):
            self.assertRaises(RuntimeError, re.match,
                r'(a+)+$', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!')

    def test_busy_loop(self):
        try:
            with timeout(0.5):
                while True:
                    pass
        except RuntimeError:
            pass
        else:
            self.fail('busy loop failed to interrupt')

    def test_IO_interrupt(self):
        """Make sure os.read() does not swallow our interruption."""
        with tempfile.NamedTemporaryFile() as tf:
            fname = tf.name
        os.mkfifo(fname)

        def writer():
            with open(fname, 'w'):
                time.sleep(2)
        threading.Thread(target=writer).start()

        try:
            fd = os.open(fname, os.O_RDONLY)
            try:
                with timeout(0.5):
                    os.read(fd, 1024)
                    self.fail('interrupt failed')
            except RuntimeError:
                pass
        finally:
            os.unlink(fname)

    def test_contextmanager_cancels_properly(self):
        """Verify that alarms get properly canceled."""
        with timeout(0.5):
            pass
        time.sleep(1)

class Outer(RuntimeError):
    pass

class Inner(RuntimeError):
    pass

class TestReentrancy(unittest.TestCase):

    def test_reentrancy_without_expiration(self):
        with timeout(1):
            with timeout(1):
                pass
        time.sleep(1.5)

    def test_inner_timeout(self):

        with timeout(1, Outer):
            with timeout(0.1, Inner):
                self.assertRaises(Inner, time.sleep, 2)
        time.sleep(1.5)

    def test_outer_timeout(self):
        with timeout(1, Outer):
            with timeout(0.1, Inner):
                pass
            self.assertRaises(Outer, time.sleep, 2)
        time.sleep(1.5)

    def test_suppressed_inner(self):
        try:
            with timeout(1, Outer):
                with timeout(1.1, Inner):
                    time.sleep(2)
        except Outer:
            pass
        time.sleep(1.5)

class TestValidation(unittest.TestCase):
    def test_timeout_value(self):

        def test(seconds):
            with timeout(seconds):
                pass
        self.assertRaises(ValueError, test, 0)
        self.assertRaises(ValueError, test, -1)

class TestThreading(unittest.TestCase):

    def test_non_main_thread(self):

        self.fail = True

        def run():
            try:
                with timeout(1):
                    pass
            except StateException:
                self.fail = False

        t = threading.Thread(target=run)
        t.start()
        t.join()
        self.assertFalse(self.fail)

if __name__ == '__main__':
    unittest.main()
