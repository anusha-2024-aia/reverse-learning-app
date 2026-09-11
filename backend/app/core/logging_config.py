import logging
import os
import sys

def setup_logging():
    """
    Sets up structured python logging for the application.
    Respects LOG_LEVEL environment variable (default: INFO).
    """
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Avoid duplicate handlers if setup_logging is called multiple times
    if not root_logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # Specific logger for application
    app_logger = logging.getLogger("reverse_learning")
    app_logger.setLevel(log_level)

    return app_logger

logger = setup_logging()

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"reverse_learning.{name}")
