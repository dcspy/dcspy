import logging


def write_log(msg: str, level: str = "INFO", stacklevel: int = 2) -> None:
    level = level.upper()
    assert level in ["INFO", "DEBUG", "ERROR"], "Invalid level for logging"

    logger = logging.getLogger()
    logger.handlers.clear()

    logging.basicConfig(format="[%(levelname)s]\t%(asctime)s\t[%(pathname)s]\t[%(lineno)s]\t\"%(message)s\"",
                        datefmt="%Y-%m-%dT%H:%M:%S%Z",
                        )

    match level:
        case "INFO":
            logger.info(msg, stacklevel=stacklevel)
        case "DEBUG":
            logger.debug(msg, stacklevel=stacklevel)
        case "ERROR":
            logger.error(msg, stacklevel=stacklevel)
        case _:
            logger.error("Invalid level for logging")


def write_debug(msg: str):
    write_log(msg, "DEBUG", stacklevel=3)


def write_error(msg: str):
    write_log(msg, "ERROR", stacklevel=3)
