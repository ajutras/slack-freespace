
import logging
import sys
from logging.handlers import RotatingFileHandler

from freespace.config import config

# Initiate logger
print("routine de logging")
logger = logging.getLogger()
logger.setLevel(config.LOGGING.LOGGER_MIN_LEVEL)

formatter = logging.Formatter(config.LOGGING.LOGGER_FORMAT,
                              style=config.LOGGING.LOGGER_FORMATTER_STYLE,
                              datefmt=config.LOGGING.LOGGER_DATE_FORMAT)


# Create terminal channel
if config.LOGGING.LOGGER_TERMINAL:
    channel_terminal = logging.StreamHandler(sys.stdout)
    channel_terminal.setLevel(config.LOGGING.LOGGER_TERMINAL_MIN_LEVEL)
    channel_terminal.setFormatter(formatter)
    logger.addHandler(channel_terminal)


# Create file channel
if config.LOGGING.LOGGER_FILE:
    channel_file = RotatingFileHandler(
        config.LOGGING.LOGGER_FILE_PATH,
        encoding=config.FREESPACE.ENCODING,
        backupCount=config.LOGGING.LOGGER_FILE_MAX_ROTATION,
        maxBytes=config.LOGGING.LOGGER_FILE_MAX_SIZE)
    channel_file.setLevel(config.LOGGING.LOGGER_FILE_MIN_LEVEL)
    channel_file.setFormatter(formatter)
    logger.addHandler(channel_file)

# TODO: add support for automatic e-mail notice when an error comes up
# http://flask.pocoo.org/docs/0.10/errorhandling/
# You can even control the output that will be sent by e-mail, check this shit out!