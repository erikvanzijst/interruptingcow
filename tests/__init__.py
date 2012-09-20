import os
import re
import tempfile
import time
import threading
import unittest

from interruptingcow import timeout, Quota, StateException

class TimeoutError(Exception):
    pass

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

@timeout(.5, exception=TimeoutError)
def sleep(seconds):
    time.sleep(seconds)

class TestDecorator(unittest.TestCase):

    def test_decorator_with_expiration(self):
        self.assertRaises(TimeoutError, sleep, 1)

    def test_decorator_without_expiration(self):
        sleep(.1)
        time.sleep(0.5) # make sure there's no delayed timeout

if __name__ == '__main__':
    unittest.main()

class TestQuota(unittest.TestCase):
    def test_remaining(self):
        q = Quota(1)
        self.assertEquals(1, q.remaining())

        q._start()
        self.assertTrue(q.running())
        time.sleep(0.5)
        q._stop()

        self.assertFalse(q.running())
        self.assertLessEqual(q.remaining(), 0.5)

    def test_nesting(self):
        q = Quota(1)

        q._start()
        self.assertTrue(q.running())
        q._start()
        self.assertTrue(q.running())
        time.sleep(0.5)
        q._stop()
        self.assertTrue(q.running())
        q._stop()
        self.assertFalse(q.running())

        self.assertLessEqual(q.remaining(), 0.5)

    def test_continuation(self):
        q = Quota(1)

        q._start()
        q._stop()
        time.sleep(0.2)
        q._start()
        q._stop()

        # tolerate a little time spent outside the sleep:
        self.assertGreater(q.remaining(), 0.9)

class TestQuotaTimeouts(unittest.TestCase):
    def test_timeout(self):
        q = Quota(1)
        with timeout(q, RuntimeError):
            time.sleep(0.2)
        self.assertTrue(0.75 < q.remaining() <= 0.8)
        time.sleep(1)
        self.assertTrue(0.75 < q.remaining() <= 0.8)
        with timeout(q, RuntimeError):
            time.sleep(0.2)
        self.assertTrue(0.55 < q.remaining() <= 0.6)

        try:
            with timeout(q, RuntimeError):
                time.sleep(0.7)
            self.fail()
        except RuntimeError:
            pass


    def test_nesting(self):
        q1 = Quota(0.5)
        q2 = Quota(1)

        try:
            with timeout(q1, Outer):
                with timeout(q2, Inner):
                    time.sleep(1)
            self.fail()
        except Outer:
            self.assertFalse(q1.running())
            self.assertLessEqual(q1.remaining(), 0.05)

            self.assertFalse(q2.running())
            self.assertTrue(0.45 < q2.remaining() <= 0.5)
