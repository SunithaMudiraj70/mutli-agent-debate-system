import logging
import sys
from logging.handlers import RotatingFileHandler

LOGFILE = "debate_log.txt"

def setup_logger():
    logger = logging.getLogger("debate")
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(ch)

    fh = RotatingFileHandler(LOGFILE, maxBytes=5_000_000, backupCount=3, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(fh)

    return logger

logger = setup_logger()
