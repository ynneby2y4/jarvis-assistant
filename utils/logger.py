"""
Logging configuration for JARVIS
"""
import logging
import logging.handlers
import os
from config import config

# Create logs directory
os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)

# Create logger
logger = logging.getLogger("jarvis")
logger.setLevel(getattr(logging, config.LOG_LEVEL))

# File handler with rotation
file_handler = logging.handlers.RotatingFileHandler(
    config.LOG_FILE,
    maxBytes=10485760,  # 10MB
    backupCount=5
)
file_handler.setLevel(getattr(logging, config.LOG_LEVEL))

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, config.LOG_LEVEL))

# Formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(f"jarvis.{name}")
