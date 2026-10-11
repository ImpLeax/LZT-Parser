"""
This module contains custom formatters for the logger.
"""

import logging
import logging.handlers
import re

from colorama import Back, Fore, Style

LOG_COLORS = {
    logging.DEBUG: Fore.BLACK + Style.BRIGHT,
    logging.INFO: Fore.GREEN,
    logging.WARN: Fore.YELLOW,
    logging.ERROR: Fore.RED,
    logging.CRITICAL: Back.RED,
}

CLI_LOG_FORMAT = (
    f"{Fore.BLACK + Style.BRIGHT}[%(asctime)s]{Style.RESET_ALL}"
    f"{Fore.CYAN}>{Style.RESET_ALL} $RESET%(levelname).1s: %(message)s{Style.RESET_ALL}"
)
CLI_TIME_FORMAT = "%d-%m-%Y %H:%M:%S"

FILE_LOG_FORMAT = "[%(asctime)s][%(filename)s][%(lineno)d]> %(levelname).1s: %(message)s"
FILE_TIME_FORMAT = "%d.%m.%y %H:%M:%S"

# Regex to clean ANSI color codes and carriage returns from the file logs
CLEAR_RE = re.compile(r"(\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~]))|(\n)|(\r)")


def add_colors(text: str) -> str:
    """
    Replaces string keywords with their corresponding color codes.

    $YELLOW - Yellow text.
    $CYAN - Light blue text.
    $MAGENTA - Purple text.
    $BLUE - Blue text.

    :param text: Original text.
    :return: Colored text.
    """
    colors = {
        "$YELLOW": Fore.YELLOW,
        "$CYAN": Fore.CYAN,
        "$MAGENTA": Fore.MAGENTA,
        "$BLUE": Fore.BLUE,
        "$GREEN": Fore.GREEN,
        "$BLACK": Fore.BLACK,
        "$WHITE": Fore.WHITE,
        "$B_YELLOW": Back.YELLOW,
        "$B_CYAN": Back.CYAN,
        "$B_MAGENTA": Back.MAGENTA,
        "$B_BLUE": Back.BLUE,
        "$B_GREEN": Back.GREEN,
        "$B_BLACK": Back.BLACK,
        "$B_WHITE": Back.WHITE,
    }
    for c in colors:
        if c in text:
            text = text.replace(c, colors[c])
    return text


class CLILoggerFormatter(logging.Formatter):
    """
    Formatter for outputting logs to the console.
    """

    def __init__(self):
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        msg = record.getMessage()
        msg = add_colors(msg)
        msg = msg.replace("$RESET", LOG_COLORS[record.levelno])
        record.msg = msg
        record.args = ()
        log_format = CLI_LOG_FORMAT.replace("$RESET", Style.RESET_ALL + LOG_COLORS[record.levelno])
        formatter = logging.Formatter(log_format, CLI_TIME_FORMAT)
        return formatter.format(record)


class FileLoggerFormatter(logging.Formatter):
    """
    Formatter for saving logs to a file without color codes.
    """

    def __init__(self):
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        msg = record.getMessage()
        msg = CLEAR_RE.sub("", msg)
        record.msg = msg
        record.args = ()
        formatter = logging.Formatter(FILE_LOG_FORMAT, FILE_TIME_FORMAT)
        return formatter.format(record)


LOGGER_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "file_formatter",
            "filename": "logs/log.log",
            "maxBytes": 20 * 1024 * 1024,  # 20 megabytes in bytes
            "backupCount": 25,  # Number of rotations to keep
            "encoding": "utf-8",
        },
        "cli_handler": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "cli_formatter",
        },
    },
    "formatters": {
        "file_formatter": {"()": "utils.logger.FileLoggerFormatter"},
        "cli_formatter": {"()": "utils.logger.CLILoggerFormatter"},
    },
    "root": {"handlers": ["cli_handler", "file_handler"], "level": "INFO"},
    "loggers": {
        "main": {"level": "DEBUG"},
        "services": {"level": "DEBUG"},
        "aiogram": {"level": "INFO"},
        "LOLZTEAM": {"level": "INFO"},
        "httpx": {"level": "WARNING"},
    },
}
