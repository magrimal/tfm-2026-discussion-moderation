"""Shared evaluation utilities.

Provides logging setup and result formatting for eval suites.
Uses the logging standard library instead of print.
"""

import logging


def setup_eval_logging(
    name: str,
    level: str = "INFO",
) -> logging.Logger:
    """Configure and return a logger for an eval suite.

    Description:
        Sets up a logger with a consistent format for eval
        output. Call once at the start of each eval module.

    Args:
        name: Logger name (typically the eval module name).
        level: Logging level string.

    Returns:
        Configured Logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
            datefmt="%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger
