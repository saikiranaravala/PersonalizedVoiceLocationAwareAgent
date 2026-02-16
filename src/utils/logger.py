"""Logging utilities for the Agentic Assistant."""

import sys
from pathlib import Path

from loguru import logger

from utils.config import config


def setup_logger():
    """Configure the application logger."""
    # Remove default handler
    logger.remove()
    
    # Get log configuration
    log_level = config.get("monitoring.log_level", "INFO")
    log_file = config.get("monitoring.log_file", "logs/agent.log")
    
    # Ensure log directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Console handler with colors (Windows compatible)
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
    )
    
    # File handler with rotation
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=log_level,
        rotation=config.get("monitoring.log_rotation", "10 MB"),
        retention="1 week",
        compression="zip",
    )
    
    logger.info("Logger initialized successfully")
    return logger


# Initialize logger on import
setup_logger()
