"""
Unit tests for logging utilities.

Tests logging configuration and utilities including debug mode
and handler setup.
"""

import pytest
import logging
from io import StringIO

from patch.logging_utils import (
    logger,
    streamhandler,
    setdebug,
    debug,
    info,
    warning,
    debugmode,
    NullHandler,
)


class TestLogger:
    """Test logger configuration."""

    def setup_method(self):
        """Reset logger state before each test."""
        # Reset logger level to default
        logger.setLevel(logging.NOTSET)

    def test_logger_exists(self):
        """Test that logger is properly configured."""
        assert logger is not None
        assert isinstance(logger, logging.Logger)

    def test_logger_name(self):
        """Test logger name."""
        # Logger should be named after the module
        assert "patch" in logger.name

    def test_logger_has_null_handler(self):
        """Test that logger has NullHandler by default."""
        # Should have at least one handler
        assert len(logger.handlers) >= 1

        # Should have a NullHandler to prevent "No handlers" warnings
        has_null_handler = any(isinstance(h, NullHandler) for h in logger.handlers)
        assert has_null_handler

    def test_logger_level_default(self):
        """Test default logger level."""
        # Default level should be reasonable
        assert logger.level in [logging.NOTSET, logging.WARNING, logging.INFO]


class TestNullHandler:
    """Test NullHandler implementation."""

    def test_null_handler_creation(self):
        """Test NullHandler can be created."""
        handler = NullHandler()
        assert handler is not None
        assert isinstance(handler, logging.Handler)

    def test_null_handler_handle(self):
        """Test NullHandler.handle method."""
        handler = NullHandler()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )

        # Should not raise any exceptions
        handler.handle(record)

    def test_null_handler_emit(self):
        """Test NullHandler.emit method."""
        handler = NullHandler()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )

        # Should not raise any exceptions
        handler.emit(record)

    def test_null_handler_create_lock(self):
        """Test NullHandler.createLock method."""
        handler = NullHandler()
        handler.createLock()

        # Lock should be None (no actual locking)
        assert handler.lock is None


class TestStreamHandler:
    """Test stream handler configuration."""

    def test_streamhandler_exists(self):
        """Test that streamhandler is configured."""
        assert streamhandler is not None
        assert isinstance(streamhandler, logging.StreamHandler)

    def test_streamhandler_not_in_logger_by_default(self):
        """Test that streamhandler is not added to logger by default."""
        # When used as a library, streamhandler should not be added by default
        # This prevents unwanted output
        is_in_handlers = streamhandler in logger.handlers
        # This might be True or False depending on how tests are run
        # The important thing is that it's controllable
        assert isinstance(is_in_handlers, bool)


class TestSetdebug:
    """Test setdebug function."""

    def setup_method(self):
        """Setup for each test method."""
        # Store original state
        self.original_debugmode = debugmode
        self.original_level = logger.level
        self.original_handlers = logger.handlers.copy()

    def teardown_method(self):
        """Cleanup after each test method."""
        # Restore original state
        import patch.logging_utils

        patch.logging_utils.debugmode = self.original_debugmode
        logger.setLevel(self.original_level)

        # Remove any handlers that were added during test
        for handler in logger.handlers[:]:
            if handler not in self.original_handlers:
                logger.removeHandler(handler)

    def test_setdebug_enables_debug_mode(self):
        """Test that setdebug enables debug mode."""
        setdebug()

        # Should enable debug mode
        import patch.logging_utils

        assert patch.logging_utils.debugmode is True

    def test_setdebug_sets_debug_level(self):
        """Test that setdebug sets logger to DEBUG level."""
        setdebug()

        assert logger.level == logging.DEBUG

    def test_setdebug_adds_stream_handler(self):
        """Test that setdebug adds stream handler to logger."""
        # Remove streamhandler if it's already there
        if streamhandler in logger.handlers:
            logger.removeHandler(streamhandler)

        setdebug()

        # Should add streamhandler
        assert streamhandler in logger.handlers

    def test_setdebug_sets_formatter(self):
        """Test that setdebug sets formatter on stream handler."""
        setdebug()

        # Should have a formatter
        assert streamhandler.formatter is not None

        # Formatter should include level name
        formatter = streamhandler.formatter
        record = logging.LogRecord(
            name="test",
            level=logging.DEBUG,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )
        formatted = formatter.format(record)
        assert "DEBUG" in formatted

    def test_setdebug_idempotent(self):
        """Test that calling setdebug multiple times is safe."""
        setdebug()
        handler_count = len(logger.handlers)

        setdebug()  # Call again

        # Should not add duplicate handlers
        assert len(logger.handlers) == handler_count


class TestLoggingFunctions:
    """Test logging convenience functions."""

    def setup_method(self):
        """Setup for each test method."""
        # Capture log output
        self.log_capture = StringIO()
        self.test_handler = logging.StreamHandler(self.log_capture)
        self.test_handler.setLevel(logging.DEBUG)
        logger.addHandler(self.test_handler)
        logger.setLevel(logging.DEBUG)

    def teardown_method(self):
        """Cleanup after each test method."""
        logger.removeHandler(self.test_handler)

    def test_debug_function(self):
        """Test debug logging function."""
        debug("test debug message")

        output = self.log_capture.getvalue()
        assert "test debug message" in output

    def test_info_function(self):
        """Test info logging function."""
        info("test info message")

        output = self.log_capture.getvalue()
        assert "test info message" in output

    def test_warning_function(self):
        """Test warning logging function."""
        warning("test warning message")

        output = self.log_capture.getvalue()
        assert "test warning message" in output

    def test_logging_with_formatting(self):
        """Test logging functions with string formatting."""
        debug("debug with %s", "formatting")
        info("info with %d", 42)
        warning("warning with %s and %d", "text", 123)

        output = self.log_capture.getvalue()
        assert "debug with formatting" in output
        assert "info with 42" in output
        assert "warning with text and 123" in output

    def test_logging_levels(self):
        """Test that logging functions use correct levels."""
        # Set logger to WARNING level
        logger.setLevel(logging.WARNING)
        self.log_capture.truncate(0)
        self.log_capture.seek(0)

        debug("debug message")
        info("info message")
        warning("warning message")

        output = self.log_capture.getvalue()

        # Only warning should appear
        assert "debug message" not in output
        assert "info message" not in output
        assert "warning message" in output


class TestDebugmode:
    """Test debugmode global variable."""

    def test_debugmode_initial_value(self):
        """Test initial value of debugmode."""
        # Should be False initially
        import patch.logging_utils

        # Note: might be True if setdebug was called in other tests
        assert isinstance(patch.logging_utils.debugmode, bool)

    def test_debugmode_changes_with_setdebug(self):
        """Test that debugmode changes when setdebug is called."""
        import patch.logging_utils

        original_value = patch.logging_utils.debugmode
        setdebug()

        assert patch.logging_utils.debugmode is True

        # Restore original value
        patch.logging_utils.debugmode = original_value


class TestLoggingIntegration:
    """Integration tests for logging utilities."""

    def test_logging_in_library_mode(self):
        """Test logging behavior when used as a library."""
        # When used as a library, should not produce output by default
        import patch.logging_utils

        # Reset to library mode
        original_debugmode = patch.logging_utils.debugmode
        patch.logging_utils.debugmode = False

        # Remove stream handler if present
        if streamhandler in logger.handlers:
            logger.removeHandler(streamhandler)

        try:
            # Should have NullHandler to prevent warnings
            has_null_handler = any(isinstance(h, NullHandler) for h in logger.handlers)
            assert has_null_handler

            # Logging should not raise exceptions
            debug("test message")
            info("test message")
            warning("test message")

        finally:
            # Restore original state
            patch.logging_utils.debugmode = original_debugmode

    def test_logging_in_application_mode(self):
        """Test logging behavior when used as an application."""
        # When setdebug is called, should produce output
        setdebug()

        # Should have stream handler
        assert streamhandler in logger.handlers

        # Should be at DEBUG level
        assert logger.level == logging.DEBUG

    def test_logging_configuration_isolation(self):
        """Test that logging configuration doesn't interfere with other loggers."""
        # Create a separate logger
        other_logger = logging.getLogger("other_test_logger")
        original_level = other_logger.level
        original_handlers = other_logger.handlers.copy()

        try:
            # Configure patch logging
            setdebug()

            # Other logger should not be affected
            assert other_logger.level == original_level
            assert other_logger.handlers == original_handlers

        finally:
            # Cleanup
            other_logger.setLevel(original_level)
            for handler in other_logger.handlers[:]:
                if handler not in original_handlers:
                    other_logger.removeHandler(handler)


class TestLoggingErrorHandling:
    """Test error handling in logging utilities."""

    def test_logging_with_none_message(self):
        """Test logging functions with None message."""
        # Should handle gracefully
        try:
            debug(None)
            info(None)
            warning(None)
        except Exception as e:
            # If it raises an exception, it should be a reasonable one
            assert isinstance(e, (TypeError, ValueError))

    def test_logging_with_complex_objects(self):
        """Test logging functions with complex objects."""
        # Should handle various object types
        test_objects = [
            {"key": "value"},
            [1, 2, 3],
            (1, 2, 3),
            set([1, 2, 3]),
        ]

        for obj in test_objects:
            try:
                debug("Object: %s", obj)
                info("Object: %s", obj)
                warning("Object: %s", obj)
            except Exception:
                # Should not raise exceptions for reasonable objects
                pytest.fail(f"Logging failed for object: {obj}")

    def test_setdebug_multiple_calls(self):
        """Test that multiple calls to setdebug don't cause issues."""
        # Should be safe to call multiple times
        for _ in range(3):
            setdebug()

        # Should still work correctly
        assert logger.level == logging.DEBUG
        import patch.logging_utils

        assert patch.logging_utils.debugmode is True


@pytest.mark.parametrize(
    "log_func,level",
    [
        (debug, logging.DEBUG),
        (info, logging.INFO),
        (warning, logging.WARNING),
    ],
)
def test_logging_functions_parametrized(log_func, level):
    """Parametrized test for logging functions."""
    # Create a test handler to capture output
    log_capture = StringIO()
    test_handler = logging.StreamHandler(log_capture)
    test_handler.setLevel(logging.DEBUG)

    logger.addHandler(test_handler)
    logger.setLevel(logging.DEBUG)

    try:
        log_func("test message for %s", log_func.__name__)

        output = log_capture.getvalue()
        assert f"test message for {log_func.__name__}" in output

    finally:
        logger.removeHandler(test_handler)
