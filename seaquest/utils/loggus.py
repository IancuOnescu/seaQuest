import logging


def init_logger(name: str, file_path: str = './seaquest.logs', level = logging.DEBUG) -> logging.Logger:
    """create an object that handles the logging

    Parameters
    ----------
    name: str
          Name of the logging object
    file_path: str
          Path of the file that stores the logs (will be created if not exists)
    level: default debug
          Logging level 

    Returns
    -------
    logger: obj
           Object that handles the logging through its inherent methods
    """
    levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "critical": logging.CRITICAL
    }

    logger = logging.getLogger(name)
    logger.setLevel(levels.get(level, logging.DEBUG))

    _init_logging_config(logger=logger, file_path=file_path)

    return logger


def _init_logging_config(logger: logging.Logger, file_path: str):
    """set the configuration of a logging object

    Set up the logging format, create the console and file handlers

    Parameters
    ----------
    logger:
           Logging object
    file_path: str
           Path of the file that stores the logs (will be created if not exists)    
    """
    console_format = logging.Formatter('[%(name)s][%(levelname)s] - %(message)s')
    file_format = logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s] - %(message)s')

    console_handler = logging.StreamHandler(); console_handler.setLevel(logging.INFO); console_handler.setFormatter(console_format)
    file_handler = logging.FileHandler(file_path, mode="a"); file_handler.setLevel(logging.DEBUG); file_handler.setFormatter(file_format)

    logger.addHandler(console_handler); logger.addHandler(file_handler)
