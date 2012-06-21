import signal
import threading
import time
from collections import namedtuple
from contextlib import GeneratorContextManager

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

    def set_sighandler():
        current = signal.getsignal(signal.SIGALRM)
        if current == signal.SIG_DFL:
            signal.signal(signal.SIGALRM, handler)
        elif current != handler:
            raise StateException('Your process alarm handler is already in '
                                 'use! Interruptingcow cannot be used in '
                                 'programs that use SIGALRM.')

    def timeout(seconds, exception):
        if seconds <= 0:
            raise ValueError('Invalid timeout: %s' % seconds)
        if threading.currentThread().name != 'MainThread':
            raise StateException('Interruptingcow can only be used from the '
                                 'MainThread.')
        set_sighandler()

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
