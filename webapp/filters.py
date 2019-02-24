import settings
from crawler.helpers import get_statuses
from crawler.models.bid import ACTIVE_STATUSES


def checkbox(value):
    if value:
        return 'checked'
    return ''


def format_time(datetime_obj):
    if datetime_obj is None:
        return '-'
    return datetime_obj.strftime(settings.DEFAULT_TIME_FORMAT)


def format_datetime(datetime_obj):
    if datetime_obj is None:
        return '-'
    return datetime_obj.strftime('{} {}'.format(
        settings.DEFAULT_TIME_FORMAT, settings.DEFAULT_DATE_FORMAT
    ))


def active_class(bid):
    is_active = bid.status in get_statuses(*ACTIVE_STATUSES)
    return 'active' if is_active else 'inactive'
