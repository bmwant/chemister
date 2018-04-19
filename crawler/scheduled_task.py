from datetime import datetime
from utils import get_minutes_value, LoggableMixin


class ScheduledTask(LoggableMixin):
    def __init__(self, *, task, scheduled_time):
        self.task = task
        self.scheduled_time = scheduled_time
        self.done = False

    def is_ready(self):
        # todo: No way! Make this comparison corrects
        time_passed = (get_minutes_value(self.scheduled_time) -
                       get_minutes_value(self.current_time)) > 0
        return not self.done and time_passed

    @property
    def current_time(self):
        return datetime.now().strftime('%H:%M')

    def __await__(self):
        # Early, to prevent double launching
        self.done = True
        self.logger.info('Running task scheduled for %s at %s',
                         self.scheduled_time, self.current_time)
        return self.task().__await__()
