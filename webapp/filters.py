import settings


def checkbox(value):
    if value:
        return 'checked'
    return ''


def format_time(datetime_obj):
    return datetime_obj.strftime(settings.DEFAULT_TIME_FORMAT)


def format_datetime(datetime_obj):
    return datetime_obj.strftime('{} {}'.format(
        settings.DEFAULT_TIME_FORMAT, settings.DEFAULT_DATE_FORMAT
    ))
