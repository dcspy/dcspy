import logging


def write_log(msg: str, level: str = "INFO", stack_level: int = 2) -> None:
    level = level.upper()
    assert level in ["INFO", "DEBUG", "ERROR"], "Invalid level for logging"

    logger = logging.getLogger()
    logger.handlers.clear()

    logging.basicConfig(format="[%(levelname)s]\t%(asctime)s\t[%(pathname)s]\t[%(lineno)s]\t\"%(message)s\"",
                        datefmt="%Y-%m-%dT%H:%M:%S%Z",
                        )

    match level:
        case "INFO":
            logger.info(msg, stacklevel=stack_level)
        case "DEBUG":
            logger.debug(msg, stacklevel=stack_level)
        case "ERROR":
            logger.error(msg, stacklevel=stack_level)
        case _:
            logger.error(f"{level} is invalid level for logging")


def write_debug(msg: str):
    write_log(msg, "DEBUG", stack_level=3)


def write_error(msg: str):
    write_log(msg, "ERROR", stack_level=3)
