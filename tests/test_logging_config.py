#!/usr/bin/env python3
"""
Tests for logging configuration module
"""

import logging
import pytest
from io import StringIO

from utils.logging_config import (
    setup_logging,
    get_logger,
    log_header,
    log_success,
    log_error,
    log_warning,
    log_info,
    log_debug,
    EmojiFormatter,
)


class TestLoggingSetup:
    """Test logging setup and configuration"""
    
    def test_setup_logging_default_level(self):
        """Test that setup_logging creates a logger with INFO level by default"""
        logger = setup_logging()
        assert logger.level == logging.INFO
    
    def test_setup_logging_custom_level(self):
        """Test that setup_logging respects custom log level"""
        logger = setup_logging(level=logging.WARNING)
        assert logger.level == logging.WARNING
    
    def test_setup_logging_verbose_mode(self):
        """Test that verbose mode sets DEBUG level"""
        logger = setup_logging(verbose=True)
        assert logger.level == logging.DEBUG
    
    def test_get_logger_without_name(self):
        """Test getting logger without a name returns root logger"""
        logger = get_logger()
        assert logger.name == "root"
    
    def test_get_logger_with_name(self):
        """Test getting logger with a specific name"""
        logger = get_logger("test_module")
        assert logger.name == "test_module"


class TestEmojiFormatter:
    """Test custom emoji formatter"""
    
    def test_emoji_formatter_adds_emoji_for_warning(self):
        """Test that formatter adds emoji for warning messages"""
        formatter = EmojiFormatter('%(message)s')
        record = logging.LogRecord(
            name="test",
            level=logging.WARNING,
            pathname="",
            lineno=0,
            msg="Test warning",
            args=(),
            exc_info=None
        )
        formatted = formatter.format(record)
        assert "⚠️" in formatted
    
    def test_emoji_formatter_adds_emoji_for_error(self):
        """Test that formatter adds emoji for error messages"""
        formatter = EmojiFormatter('%(message)s')
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="Test error",
            args=(),
            exc_info=None
        )
        formatted = formatter.format(record)
        assert "❌" in formatted
    
    def test_emoji_formatter_skips_duplicate_emoji(self):
        """Test that formatter doesn't add duplicate emoji for messages that already have them"""
        formatter = EmojiFormatter('%(message)s')
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="🗺️ Map message",
            args=(),
            exc_info=None
        )
        formatted = formatter.format(record)
        # Should not add extra ℹ️ emoji
        assert formatted == "🗺️ Map message"


class TestConvenienceFunctions:
    """Test convenience logging functions"""
    
    def test_log_info(self, caplog):
        """Test log_info function"""
        with caplog.at_level(logging.INFO):
            log_info("Test info message")
        assert "Test info message" in caplog.text
    
    def test_log_warning(self, caplog):
        """Test log_warning function"""
        with caplog.at_level(logging.WARNING):
            log_warning("Test warning message")
        assert "Test warning message" in caplog.text
    
    def test_log_error(self, caplog):
        """Test log_error function"""
        with caplog.at_level(logging.ERROR):
            log_error("Test error message")
        assert "Test error message" in caplog.text
    
    def test_log_debug(self, caplog):
        """Test log_debug function"""
        with caplog.at_level(logging.DEBUG):
            log_debug("Test debug message")
        assert "Test debug message" in caplog.text
    
    def test_log_success(self, caplog):
        """Test log_success function"""
        with caplog.at_level(logging.INFO):
            log_success("Operation completed")
        assert "✓ Operation completed" in caplog.text
    
    def test_log_header(self, caplog):
        """Test log_header function"""
        with caplog.at_level(logging.INFO):
            log_header("Test Header", char="=", width=20)
        assert "Test Header" in caplog.text
        assert "=" * 20 in caplog.text


class TestLoggingIntegration:
    """Integration tests for logging system"""
    
    def test_logging_levels_hierarchy(self):
        """Test that log level hierarchy works correctly"""
        # Set to WARNING level
        logger = setup_logging(level=logging.WARNING)
        
        # Create a string buffer to capture output
        import io
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.WARNING)
        logger.addHandler(handler)
        
        # These should be logged
        logger.warning("Warning message")
        logger.error("Error message")
        
        # These should NOT be logged
        logger.info("Info message")
        logger.debug("Debug message")
        
        output = log_stream.getvalue()
        assert "Warning message" in output
        assert "Error message" in output
        assert "Info message" not in output
        assert "Debug message" not in output
