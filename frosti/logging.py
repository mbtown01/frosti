import logging
from sys import exc_info
from traceback import format_exception
from queue import Queue

from logging.handlers import QueueHandler

# install the root logger
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(module)s %(levelname)s - %(message)s',
    # handlers=[RotatingFileHandler('frosti.log')],
)

# create logger
log = logging.getLogger('frosti')

logging.getLogger('chardet.charsetprober').setLevel(logging.INFO)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.engine.base.Engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.dialects').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.orm').setLevel(logging.WARNING)


def setupLogging(queue: Queue = None):
    if queue is None:
        handler = logging.StreamHandler()
    else:
        handler = QueueHandler(queue)

    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(module)s %(levelname)s - %(message)s'))
    logging.getLogger('').addHandler(handler)


def handleException(origin: str):
    exc_type, exc_value, exc_traceback = exc_info()
    lines = format_exception(
        exc_type, exc_value, exc_traceback)
    log.warning(f"{origin} encountered exception:")
    for line in lines:
        log.warning(f"{line.rstrip()}")
