import typing

from datetime import datetime, timedelta
from utils import make_datetime, LoggableMixin


class ScheduledTask(LoggableMixin):
    def __init__(self, *, task: typing.Callable, scheduled_time):
        self.task = task
        self.scheduled_time = scheduled_time
        self._scheduled_time = make_datetime(scheduled_time)
        self.done = False

    def is_ready(self):
        time_passed = datetime.now() >= self._scheduled_time
        return not self.done and time_passed

    def _reschedule(self):
        """
        Reschedule execution for the next day.
        """
        self._scheduled_time += timedelta(days=1)

    @property
    def current_time(self):
        return datetime.now().strftime('%H:%M')

    def __await__(self):
        # Early, to prevent double launching
        self.done = True
        self._reschedule()
        self.logger.info('Running task scheduled for %s at %s',
                         self.scheduled_time, self.current_time)
        return self.task().__await__()
