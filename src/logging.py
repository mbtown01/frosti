import logging

from logging.handlers import QueueHandler, RotatingFileHandler
from queue import Queue

# install the root logger
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(module)s %(levelname)s - %(message)s',
    handlers=[RotatingFileHandler('rpt.log')],
)

# create logger
log = logging.getLogger('rpt')


def setupLogging(queue: Queue=None):
    if queue is None:
        handler = logging.StreamHandler()
    else:
        handler = QueueHandler(queue)

    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(module)s %(levelname)s - %(message)s'))
    logging.getLogger('').addHandler(handler)

    logging.getLogger('chardet.charsetprober').setLevel(logging.INFO)
