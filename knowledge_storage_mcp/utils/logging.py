"""
Logging module for the Knowledge Storage MCP.

This module provides a consistent logging setup for the MCP.
"""

import logging
import os
import sys
from typing import Optional

def setup_logging(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Set up a logger with a consistent format.
    
    Args:
        name (str): Name of the logger
        level (Optional[int]): Logging level (defaults to environment variable or INFO)
    
    Returns:
        logging.Logger: Configured logger
    """
    # Determine logging level from environment variable or default to INFO
    if level is None:
        level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
        level = getattr(logging, level_name, logging.INFO)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
    
    return logger
