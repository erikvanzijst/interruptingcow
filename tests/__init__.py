import time
import threading
import unittest

from interruptingcow import start_watchdog, stop_watchdog, interruptingcow
from interruptingcow import InterruptedException, StateException

class TestInterrupt(unittest.TestCase):

    def tearDown(self):
        stop_watchdog()

    def test_interrupt(self):
        start_watchdog(timeout=1)
        self.assertRaises(InterruptedException, time.sleep, 2)

    def test_stop_watchdog(self):
        """Verify that stop_watchdog() really cancels the alarm."""
        start_watchdog(timeout=1)
        stop_watchdog()
        time.sleep(1.5)

    def test_contextmanager(self):
        try:
            with interruptingcow(timeout=1):
                time.sleep(1.5)
                self.fail('interrupt failed')
        except InterruptedException:
            pass

    def test_contextmanager_cancels_properly(self):
        with interruptingcow(timeout=1):
            pass
        time.sleep(1.5)

class TestReentrancy(unittest.TestCase):

    def tearDown(self):
        stop_watchdog()

    def test_reentrancy(self):
        start_watchdog()
        try:
            start_watchdog()
            self.fail('Should not allow reentrancy')
        except StateException:
            pass

class TestThreading(unittest.TestCase):

    def test_non_main_thread(self):

        self.fail = True

        def run():
            try:
                start_watchdog()
            except StateException:
                self.fail = False

        t = threading.Thread(target=run)
        t.start()
        t.join()
        self.assertFalse(self.fail)

if __name__ == '__main__':
    unittest.main()
