import logging

from logging.handlers import QueueHandler
from queue import Queue

# create logger
log = logging.getLogger('rpt')


def setupLogging(queue: Queue=None):
    # log.setLevel(logging.DEBUG)

    # # create formatter
    # formatter = logging.Formatter(
    #     '[%(asctime)s] %(levelname)s - %(message)s')

    if queue is None:
        handler = logging.StreamHandler()
    else:
        handler = QueueHandler(queue)

    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] %(module)s %(levelname)s - %(message)s',
        handlers=[handler],
    )
