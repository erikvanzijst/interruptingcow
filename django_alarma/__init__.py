import logging
import signal

from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed

logger = logging.getLogger(__name__)
timeout = int(getattr(settings, 'ALARMA_TIMER', 25))

class InterruptedException(Exception):
    def __init__(self, timeout):
        super(InterruptedException, self).__init__()
        self.timeout = timeout

def handler(signum, frame):
    raise InterruptedException(timeout)

class AlarmaMiddleware(object):

    disabled = False

    def __init__(self):
        if not getattr(settings, 'ALARMA', True):
            raise MiddlewareNotUsed
        self.orig_handler = signal.SIG_DFL

    def process_request(self, request):

        self.orig_handler = signal.getsignal(signal.SIGALRM)
        if self.orig_handler not in (handler, signal.SIG_DFL):
            logger.warning('Your process alarm handler is already in use! '
                           'Disabling Alarma.')
            self.disabled = True

        if not self.disabled:
            try:
                signal.signal(signal.SIGALRM, handler)
            except ValueError:
                logger.error('Unable to register SIGARLM handler; '
                             'Alarma disabled.', exc_info=1)
                self.disabled = True
            else:
                if signal.alarm(timeout):
                    logger.warning('Your process alarm handler is already in use! '
                                   'Disabling Alarma.')
                    self.disabled = True

    def process_response(self, request, response):
        if not self.disabled:
            signal.alarm(0)
            try:
                signal.signal(signal.SIGALRM, self.orig_handler)
            except ValueError:
                logger.error('Unable to restore the previous signal.SIGALRM '
                             'handler', exc_info=1)
        return response
