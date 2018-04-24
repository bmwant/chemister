

def checkbox(value):
    if value:
        return 'checked'
    return ''


def format_time(datetime_obj):
    return datetime_obj.strftime('%H:%M')


def format_datetime(datetime_obj):
    return datetime_obj.strftime('%H:%M %d/%m/%y')
