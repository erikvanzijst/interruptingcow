import signal
import threading
import time
from collections import namedtuple
from contextlib import contextmanager

class StateException(Exception):
    pass

def _bootstrap():

    Timer = namedtuple('Timer', 'expiration exception')
    timers = []

    def handler(*args):
        exception = timers.pop().exception
        if timers:
            timeleft = timers[-1].expiration - time.time()
            if timeleft > 0:
                signal.setitimer(signal.ITIMER_REAL, timeleft)
            else:
                handler(*args)

        raise exception

    @contextmanager
    def timeout(seconds, exception=RuntimeError):
        if seconds <= 0:
            raise ValueError('Invalid timeout: %s' % seconds)
        if threading.currentThread().name != 'MainThread':
            raise StateException('Timeouts can only be set on the MainThread')

        depth = len(timers)
        timeleft = signal.getitimer(signal.ITIMER_REAL)[0]
        if not timers or timeleft > seconds:
            try:
                signal.setitimer(signal.ITIMER_REAL, seconds)
                timers.append(Timer(time.time() + seconds, exception))
                yield
            finally:
                if len(timers) > depth:
                    # cancel our timer
                    signal.setitimer(signal.ITIMER_REAL, 0)
                    timers.pop()
                    if timers:
                        # reinstall the parent timer
                        timeleft = timers[-1].expiration - time.time()
                        if timeleft > 0:
                            signal.setitimer(signal.ITIMER_REAL, timeleft)
                        else:
                            # the parent timer has expired, trigger the handler
                            handler()
        else:
            # not enough time left on the parent timer
            yield

    if signal.getsignal(signal.SIGALRM) != signal.SIG_DFL:
        raise StateException('Your process alarm handler is already in use! '
                             'Interruptingcow cannot be used in programs that '
                             'use SIGALRM.')
    else:
        signal.signal(signal.SIGALRM, handler)
        return timeout

timeout = _bootstrap()
