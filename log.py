import logging
from logging.handlers import TimedRotatingFileHandler
import os
from datetime import datetime
from config import settings
from typing import Dict

class Logger:
    """
    A utility class for creating and managing logger instances.
    """
    _loggers: Dict[str, logging.Logger] = {}

    @staticmethod
    def get_logger(log_name: str = 'app') -> logging.Logger:
        """
        Retrieves a logger instance by name. If the logger does not exist, it creates a new one.
        The logger is configured to write logs to both the console and a file, with the file logs
        organized into directories by date.

        :param log_name: The name of the logger to retrieve or create.
        :return: A configured logger instance.
        """
        if log_name in Logger._loggers:
            return Logger._loggers[log_name]

        # Log directory fixed to 'logs' under the current directory
        base_dir = 'logs'
        if not os.path.exists(base_dir):
            os.makedirs(base_dir, mode=0o777, exist_ok=True)

        # Log file name
        log_file = os.path.join(base_dir, f"{log_name}.log")

        # Create logger
        logger = logging.getLogger(log_name)
        logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all levels of logs

        # Create console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)  # Set to DEBUG to capture all levels of logs

        # Create file handler with expiration period imported from config.settings
        fh = TimedRotatingFileHandler(log_file, when='h', interval=settings.LOG_ROTATE_INTERVAL, backupCount=settings.LOG_BACKUP_COUNT)
        fh.setLevel(logging.DEBUG)  # Set to DEBUG to capture all levels of logs

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)

        # Add handlers to logger
        logger.addHandler(ch)
        logger.addHandler(fh)

        Logger._loggers[log_name] = logger
        return logger