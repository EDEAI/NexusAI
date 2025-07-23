import logging

from dify_plugin.config.logger_format import plugin_logger_handler


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(plugin_logger_handler)
    return logger
