"""
Logging utilities for the patch module.

Copyright (c) 2008-2016 anatoly techtonik
Available under the terms of MIT license
"""

import logging


class NullHandler(logging.Handler):
    """A logging handler that discards all log records.

    This handler is used as a default to prevent the "No handlers could be
    found for logger" warning when the patch module is used as a library
    without explicit logging configuration.

    Originally copied from Python 2.7 for compatibility.
    See: http://bugs.python.org/issue16539

    Example:
        >>> import logging
        >>> logger = logging.getLogger('mylogger')
        >>> logger.addHandler(NullHandler())  # Silence all logging

    Note:
        This handler effectively disables logging output unless
        other handlers are explicitly added to the logger.
    """

    def handle(self, record: logging.LogRecord) -> bool:
        """Handle a log record by doing nothing.

        Args:
            record (logging.LogRecord): Log record to handle.

        Returns:
            bool: Always returns True to indicate the record was handled.
        """
        return True

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record by doing nothing.

        Args:
            record (logging.LogRecord): Log record to emit.
        """
        pass

    def createLock(self) -> None:
        """Create a lock for thread safety by setting it to None.

        Since this handler does nothing, no actual locking is needed.
        """
        self.lock = None


# Logging is controlled by logger named after the
# module name (e.g. 'patch' for patch.py module)
logger = logging.getLogger(
    __name__.split(".")[0]
)  # Get 'patch' from 'patch.logging_utils'

debug = logger.debug
info = logger.info
warning = logger.warning

streamhandler = logging.StreamHandler()

# initialize logger itself
logger.addHandler(NullHandler())

debugmode = False


def setdebug() -> None:
    """Enable debug logging for the patch module.

    Configures the logger to output debug messages to stderr with a
    formatted layout. This is useful for troubleshooting patch parsing
    and application issues.

    Effects:
        - Sets global debugmode flag to True
        - Sets logger level to DEBUG
        - Adds stream handler if not already present
        - Configures log format to show level and message

    Example:
        >>> import patch
        >>> patch.setdebug()  # Enable debug output
        >>> patchset = patch.fromfile('test.patch')
           DEBUG reading test.patch
           DEBUG total files: 1  total hunks: 2

    Note:
        When used as a library, the stream handler is only added
        when debug mode is explicitly enabled to avoid unwanted output.
    """
    global debugmode

    debugmode = True
    loglevel = logging.DEBUG
    logformat = "%(levelname)8s %(message)s"
    logger.setLevel(loglevel)

    if streamhandler not in logger.handlers:
        # when used as a library, streamhandler is not added
        # by default
        logger.addHandler(streamhandler)

    streamhandler.setFormatter(logging.Formatter(logformat))
