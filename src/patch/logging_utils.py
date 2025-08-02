"""
Logging utilities for the patch module.

Copyright (c) 2008-2016 anatoly techtonik
Available under the terms of MIT license
"""
import logging


class NullHandler(logging.Handler):
    """Copied from Python 2.7 to avoid getting
    `No handlers could be found for logger "patch"`
    http://bugs.python.org/issue16539
    """
    def handle(self, record):
        pass

    def emit(self, record):
        pass

    def createLock(self):
        self.lock = None


# Logging is controlled by logger named after the
# module name (e.g. 'patch' for patch.py module)
logger = logging.getLogger(__name__.split('.')[0])  # Get 'patch' from 'patch.logging_utils'

debug = logger.debug
info = logger.info
warning = logger.warning

streamhandler = logging.StreamHandler()

# initialize logger itself
logger.addHandler(NullHandler())

debugmode = False


def setdebug():
    global debugmode, streamhandler

    debugmode = True
    loglevel = logging.DEBUG
    logformat = "%(levelname)8s %(message)s"
    logger.setLevel(loglevel)

    if streamhandler not in logger.handlers:
        # when used as a library, streamhandler is not added
        # by default
        logger.addHandler(streamhandler)

    streamhandler.setFormatter(logging.Formatter(logformat))
