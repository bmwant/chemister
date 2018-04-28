import logging
from datetime import datetime

import coloredlogs


FORMAT = '%(asctime)s [%(name)s] %(levelname)s:%(message)s'
DATE_FORMAT = '%H:%M:%S %d-%m-%y'
FORMATTER = logging.Formatter(fmt=FORMAT, datefmt=DATE_FORMAT)


def get_logger(name='default', level=logging.DEBUG, colored=False):
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(fmt=FORMATTER)
        logger.addHandler(handler)

    if colored:
        coloredlogs.install(level=level, logger=logger)

    return logger


class LoggableMixin(object):
    @property
    def logger(self):
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__.lower())

        return self._logger


def get_midnight(datetime_value):
    return datetime_value.replace(hour=0, minute=0, second=0, microsecond=0)


def get_hours_and_minutes(scheduled_time):
    hours, mins = map(int, scheduled_time.split(':'))
    return hours, mins


def make_datetime(time_spec: str):
    """
    Create datetime object for current day from time specification.
    """
    hours, minutes = get_hours_and_minutes(time_spec)
    daily_datetime = datetime.now()
    datetime_from_spec = daily_datetime.replace(hour=hours, minute=minutes)
    return datetime_from_spec
