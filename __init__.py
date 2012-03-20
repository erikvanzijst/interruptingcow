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

    def process_request(self, request):

        if signal.getsignal(signal.SIGALRM) not in (handler, signal.SIG_DFL):
            logger.warning('Your process alarm handler is already in use! '
                           'Disabling Alarma.')
            self.disabled = True

        if not self.disabled:
            signal.signal(signal.SIGALRM, handler)
            if signal.alarm(timeout):
                logger.warning('Your process alarm handler is already in use! '
                               'Disabling Alarma.')

    def process_response(self, request, response):
        if not self.disabled:
            signal.alarm(0)
        return response
