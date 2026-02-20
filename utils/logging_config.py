#!/usr/bin/env python3
"""
Centralized Logging Configuration for My Local Map

Provides a consistent logging setup across all modules with:
- Colored console output with emoji for better readability
- Configurable log levels
- Consistent formatting
- Support for verbose/debug modes
"""

import logging
import sys
from typing import Optional

# Emoji mappings for log levels (maintaining existing output style)
LEVEL_EMOJIS = {
    logging.DEBUG: "🔍",
    logging.INFO: "ℹ️ ",
    logging.WARNING: "⚠️ ",
    logging.ERROR: "❌",
    logging.CRITICAL: "🚨",
}


class EmojiFormatter(logging.Formatter):
    """Custom formatter that adds emoji prefixes to log messages"""

    def format(self, record):
        # Add emoji prefix based on level
        emoji = LEVEL_EMOJIS.get(record.levelno, "")

        # For INFO level, check if message already has an emoji
        if record.levelno == logging.INFO:
            # Common emoji used in existing code
            existing_emojis = [
                "🗺️",
                "📍",
                "📏",
                "🎯",
                "📁",
                "🔄",
                "🎨",
                "🖼️",
                "⛰️",
                "🏔️",
                "✓",
                "🎉",
                "📄",
                "📐",
            ]
            if any(record.msg.startswith(e) for e in existing_emojis):
                emoji = ""  # Don't add duplicate emoji

        if emoji:
            record.msg = f"{emoji} {record.msg}"

        return super().format(record)


def setup_logging(level: int = logging.INFO, verbose: bool = False) -> logging.Logger:
    """
    Configure logging for the application.

    Args:
        level: Base logging level (default: INFO)
        verbose: Enable verbose output (sets DEBUG level)

    Returns:
        Logger instance configured for the application
    """
    # Use DEBUG level if verbose is enabled
    if verbose:
        level = logging.DEBUG

    # Configure root logger
    root_logger = logging.getLogger()

    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    root_logger.setLevel(level)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Create formatter - simpler format to match existing output style
    formatter = EmojiFormatter("%(message)s")
    console_handler.setFormatter(formatter)

    # Add handler to root logger
    root_logger.addHandler(console_handler)

    return root_logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Logger name (typically __name__ of the calling module)

    Returns:
        Logger instance
    """
    if name is None:
        return logging.getLogger()
    return logging.getLogger(name)


# Convenience functions that match existing print() patterns
def log_header(message: str, char: str = "=", width: int = 50):
    """Log a header with decorative line (replaces print with separator)"""
    logger = get_logger()
    logger.info(message)
    logger.info(char * width)


def log_success(message: str):
    """Log a success message"""
    logger = get_logger()
    logger.info(f"✓ {message}")


def log_error(message: str):
    """Log an error message"""
    logger = get_logger()
    logger.error(message)


def log_warning(message: str):
    """Log a warning message"""
    logger = get_logger()
    logger.warning(message)


def log_info(message: str):
    """Log an info message"""
    logger = get_logger()
    logger.info(message)


def log_debug(message: str):
    """Log a debug message"""
    logger = get_logger()
    logger.debug(message)
