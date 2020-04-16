import datetime


def to_datetime(dt_str):
    return datetime.datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S.%fZ")


def get_date(attr_name, data):
    date = data.get(attr_name, None)
    if date is None:
        return date
    return to_datetime(date)
