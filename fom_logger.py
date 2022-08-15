import logging
from sys import stdout


def logger():
    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)
    logFormatter = logging.Formatter("%(asctime)s %(message)s")
    consoleHandler = logging.StreamHandler(stdout)
    consoleHandler.setFormatter(logFormatter)
    fileHandler = logging.FileHandler(filename="bot.log", encoding="utf-8", mode="a")
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.addHandler(fileHandler)

    return logger


logger = logger()
