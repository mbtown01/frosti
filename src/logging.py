import logging

from logging.handlers import QueueHandler
from queue import Queue

# create logger
log = logging.getLogger('rpt')


def setupLogging(queue: Queue):
    log.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s - %(message)s')

    if queue is None:
        streamHandler = logging.StreamHandler()
        streamHandler.setLevel(logging.DEBUG)
        streamHandler.setFormatter(formatter)
        log.addHandler(streamHandler)
    else:
        queueHandler = QueueHandler(queue)
        queueHandler.setLevel(logging.DEBUG)
        queueHandler.setFormatter(formatter)
        log.addHandler(queueHandler)
