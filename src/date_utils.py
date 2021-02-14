from datetime import datetime
from matplotlib import dates


def str_to_datetime(s):
    iso_datetime = s.replace('T', ' ').split('.')[0]
    return datetime.fromisoformat(iso_datetime)


def datetime_to_num(date):
    return dates.date2num(date)


def num_to_datetime(num):
    return dates.num2date(num).replace(tzinfo=None)


def is_same_day(date1, date2):
    if not isinstance(date1, datetime):
        date1 = num_to_datetime(date1)

    if not isinstance(date2, datetime):
        date2 = num_to_datetime(date2)

    return date1.strftime('%Y%m%d') == date2.strftime('%Y%m%d')
