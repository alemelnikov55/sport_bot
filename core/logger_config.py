import os
import sys
from datetime import datetime

logger_name = "project"
today_str = datetime.now().strftime("%Y-%m-%d")
log_dir = os.path.dirname(__file__)
log_file_path = os.path.join(log_dir, f"{logger_name}_{today_str}.log")

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "colored": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s%(levelname)s | %(name)s | %(asctime)s | %(lineno)d | %(message)s",
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        },
        "default": {
            "format": "%(levelname)s | %(name)s | %(asctime)s | %(lineno)d | %(message)s",
            "datefmt": "%H:%M:%S"
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "colored",
            "stream": sys.stdout,
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "DEBUG",
            "formatter": "default",
            "filename": log_file_path,
            "when": "midnight",
            "backupCount": 10,
            "encoding": "utf-8",
            "utc": False,
        },
    },

    "root": {
        "level": "INFO",
        "handlers": ["console", "file"]
    },
}