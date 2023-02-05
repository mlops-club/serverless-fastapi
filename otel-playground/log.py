from logging import getLogger

LOGGER = getLogger(__name__)


LOGGER.debug("This is a debug message")
LOGGER.info("This is an info message")
LOGGER.warning("This is a warning message")
LOGGER.error("This is an error message")
LOGGER.critical("This is a critical message")

try:
    1 / 0
except ZeroDivisionError:
    LOGGER.exception("This is an exception message")
