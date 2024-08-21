import logging

logger = logging.getLogger()


def write_log(msg: str, level: str = "INFO", stack_level: int = 2) -> None:
    level = level.upper()
    match level:
        case "INFO":
            logger.info(msg, stacklevel=stack_level)
        case "DEBUG":
            logger.debug(msg, stacklevel=stack_level)
        case "ERROR":
            logger.error(msg, stacklevel=stack_level)
        case "WARNING":
            logger.warning(msg, stacklevel=stack_level)
        case _:
            logger.error(f"{level} is invalid level for logging")


def write_info(msg: str):
    write_log(msg, "INFO", stack_level=3)


def write_debug(msg: str):
    write_log(msg, "DEBUG", stack_level=3)


def write_error(msg: str):
    write_log(msg, "ERROR", stack_level=3)


def write_warning(msg: str):
    write_log(msg, "WARNING", stack_level=3)
