from functools import wraps, partial
import logging
import signal

class State(object):
    uninitialized = 0
    enabled = 1
    disabled = 2

logger = logging.getLogger(__name__)
state = State.uninitialized

def handler(timeout, signum, frame):
    raise InterruptedException(timeout)

class InterruptedException(Exception):
    def __init__(self, timeout):
        super(InterruptedException, self).__init__()
        self.timeout = timeout

def pre_request(worker, req, timeout=25):
    global state

    if state == State.uninitialized:
        if signal.getsignal(signal.SIGALRM) != signal.SIG_DFL:
            print('Your process alarm handler is already in use! '
                           'Disabling Alarma: ' + repr(signal.getsignal(signal.SIGALRM)))
            state = State.disabled
        else:
            try:
                print 'Registering handler...'
                signal.signal(signal.SIGALRM, partial(handler, timeout))
                state = State.enabled
            except ValueError:
                print('Unable to register SIGARLM handler; '
                             'Alarma disabled.')
                state = State.disabled

    if state == State.enabled:
        signal.alarm(timeout)

def post_request(worker, req, environ):
    if state == State.enabled:
        signal.alarm(0)

def start_watchdog(*args, **kwargs):
    parameterized = len(args) != 1 or not callable(args[0])
    timeout = kwargs.get('timeout', 25)

    def decorator(func):
        if func.__name__ != 'pre_request':
            raise AssertionError("Use this decorator on Gunicorn's pre_request() hook.")
        @wraps(func)
        def wrapped_function(worker, req):
            pre_request(worker, req, timeout=timeout)
            return func(worker, req)
        return wrapped_function

    return decorator if parameterized else decorator(args[0])

def end_watchdog(func):
    if func.__name__ != 'post_request':
        raise AssertionError("Use this decorator on Gunicorn's post_request() hook.")
    @wraps(func)
    def wrapped_function(worker, req, environ):
        post_request(worker, req, environ)
        return func(worker, req, environ)
    return wrapped_function
