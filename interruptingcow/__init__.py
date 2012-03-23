from contextlib import contextmanager
import signal

_timeout = 0.0

class InterruptedException(Exception):
    def __init__(self, timeout):
        super(InterruptedException, self).__init__()
        self.timeout = timeout

class StateException(Exception):
    pass

def start_watchdog(timeout=25):

    if int(timeout) <= 0:
        raise ValueError('Use a timeout value greater than 0')

    elif signal.getsignal(signal.SIGALRM) != signal.SIG_DFL:
        raise StateException('Your process alarm handler is already in use! '
                             'Interruptingcow is not reentrant and not '
                             'compatible with programs that use SIGALRM.')
    else:
        global _timeout
        _timeout = int(timeout)
        def handler(signum, frame):
            try:
                stop_watchdog()
            except Exception:
                pass
            finally:
                raise InterruptedException(_timeout)

        try:
            signal.signal(signal.SIGALRM, handler)
        except ValueError:
            raise StateException('Unable to register SIGARLM handler')
        else:
            signal.alarm(_timeout)

def stop_watchdog():

    global _timeout
    if _timeout:
        try:
            # reset signal handler
            signal.signal(signal.SIGALRM, signal.SIG_DFL)
            signal.alarm(0)
        finally:
            _timeout = None

@contextmanager
def interruptingcow(timeout=25):

    start_watchdog(timeout=timeout)
    try:
        yield
    finally:
        stop_watchdog()
