"""Logger factory: returns a named logger writing INFO+ to stdout."""
import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """Returns a named logger that writes INFO+ to stdout."""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(handler)
    return logger
