import logging


def write_log(msg: str, level: str = "INFO") -> None:
    level = level.upper()
    assert level in ["INFO", "DEBUG", "ERROR"], "Invalid level for logging"

    logger = logging.getLogger()
    logger.handlers.clear()

    logging.basicConfig(format="[%(levelname)s]\t%(asctime)s\t[%(pathname)s]\t[%(lineno)s]\t\"%(message)s\"",
                        datefmt="%Y-%m-%dT%H:%M:%S%Z",
                        level=logging.INFO)

    match level:
        case "INFO":
            logger.info(msg, stacklevel=2)
        case "DEBUG":
            logger.debug(msg, stacklevel=2)
        case "ERROR":
            logger.error(msg, stacklevel=2)
        case _:
            logger.error("Invalid level for logging")
