import signal
import threading
import time
from collections import namedtuple
from contextlib import GeneratorContextManager

class StateException(Exception):
    pass

class Quota(object):
    def __init__(self, seconds):
        if seconds <= 0:
            raise ValueError('Invalid timeout: %s' % seconds)
        else:
            self._timeleft = seconds
        self._depth = 0
        self._starttime = None

    def _start(self):
        if self._depth is 0:
            self._starttime = time.time()
        self._depth += 1

    def _stop(self):
        if self._depth is 1:
            self._timeleft = self.remaining()
            self._starttime = None
        self._depth -= 1

    def running(self):
        return self._depth > 0

    def remaining(self):
        if self.running():
            return max(self._timeleft - (time.time() - self._starttime), 0)
        else:
            return max(self._timeleft, 0)

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

    def set_sighandler():
        current = signal.getsignal(signal.SIGALRM)
        if current == signal.SIG_DFL:
            signal.signal(signal.SIGALRM, handler)
        elif current != handler:
            raise StateException('Your process alarm handler is already in '
                                 'use! Interruptingcow cannot be used in '
                                 'programs that use SIGALRM.')

    def timeout(seconds, exception):
        if threading.currentThread().name != 'MainThread':
            raise StateException('Interruptingcow can only be used from the '
                                 'MainThread.')
        if isinstance(seconds, Quota):
            quota = seconds
        else:
            quota = Quota(seconds)
        set_sighandler()
        seconds = quota.remaining()

        depth = len(timers)
        parenttimeleft = signal.getitimer(signal.ITIMER_REAL)[0]
        if not timers or parenttimeleft > seconds:
            try:
                quota._start()
                timers.append(Timer(time.time() + seconds, exception))
                if seconds > 0:
                    signal.setitimer(signal.ITIMER_REAL, seconds)
                    yield
                else:
                    handler()
            finally:
                quota._stop()
                if len(timers) > depth:
                    # cancel our timer
                    signal.setitimer(signal.ITIMER_REAL, 0)
                    timers.pop()
                    if timers:
                        # reinstall the parent timer
                        parenttimeleft = timers[-1].expiration - time.time()
                        if parenttimeleft > 0:
                            signal.setitimer(signal.ITIMER_REAL, parenttimeleft)
                        else:
                            # the parent timer has expired, trigger the handler
                            handler()
        else:
            # not enough time left on the parent timer
            try:
                quota._start()
                yield
            finally:
                quota._stop()

    class Timeout(GeneratorContextManager):
        """This class allows us to use timeout() both as an inline
        with-statement, as well as a function decorator.

        To this end, it implements both the contextmanager's __enter__() and
        __exit__() methods, as well as the function decorator class' __call__()
        method.
        """
        def __init__(self, seconds, exception=RuntimeError):
            super(Timeout, self).__init__(None)
            self._seconds = seconds
            self._exception = exception

        def __enter__(self):
            self.gen = timeout(self._seconds, self._exception)
            return super(Timeout, self).__enter__()

        def __call__(self, func):
            def inner(*args, **kwargs):
                with self:
                    return func(*args, **kwargs)
            return inner

    return Timeout

timeout = _bootstrap()
