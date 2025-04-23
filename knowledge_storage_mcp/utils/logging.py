"""
Logging configuration for the Knowledge Storage MCP.

This module provides a consistent logging setup across the MCP server,
with configurable log levels and formatting.
"""

import logging
import os
import sys
from typing import Optional

from pythonjsonlogger import jsonlogger

# Get log level from environment or use default
DEFAULT_LOG_LEVEL = "INFO"
LOG_LEVEL = os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL).upper()

# Configure log level mapping
LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# Get numeric log level
NUMERIC_LOG_LEVEL = LOG_LEVEL_MAP.get(LOG_LEVEL, logging.INFO)

# Configure log format for JSON logging
JSON_LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s %(message)s"

def setup_logging(module_name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Configure and return a logger for the specified module.
    
    Args:
        module_name: Name of the module for the logger
        level: Log level (if None, use environment or default)
    
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(module_name)
    
    # Set log level
    if level is not None:
        numeric_level = LOG_LEVEL_MAP.get(level.upper(), logging.INFO)
    else:
        numeric_level = NUMERIC_LOG_LEVEL
    
    logger.setLevel(numeric_level)
    
    # Remove existing handlers if any
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatters
    json_formatter = jsonlogger.JsonFormatter(JSON_LOG_FORMAT)
    stream_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(stream_formatter)
    
    # Create file handler if log directory exists
    log_dir = os.path.join(os.getcwd(), "logs")
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except Exception:
            # Skip file logging if can't create directory
            pass
    
    if os.path.exists(log_dir):
        log_file = os.path.join(log_dir, f"{module_name.replace('.', '_')}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(json_formatter)
        logger.addHandler(file_handler)
    
    # Add console handler
    logger.addHandler(console_handler)
    
    # Set propagation
    logger.propagate = False
    
    return logger
