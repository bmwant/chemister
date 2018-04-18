import logging
import coloredlogs


FORMAT = '[%(name)s] %(levelname)s:%(message)s'
FORMATTER = logging.Formatter(fmt=FORMAT)


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


def get_minutes_value(scheduled_time):
    hours, mins = map(int, scheduled_time.split(':'))
    return hours*60 + mins
