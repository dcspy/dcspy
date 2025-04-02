import logging


def get_logger():
    logger_ = logging.getLogger(__name__)
    return logger_


logger = get_logger()
