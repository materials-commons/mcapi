import re
import datetime

re1 = re.compile(r"\s+")
re2 = re.compile(r"/+")


def _normalise_property_name(name):
    if name:
        name = name.replace('-', '_')
        name = re1.sub("_", name)
        name = re2.sub("_", name)
        name = name.lower()
    return name


def _convert_for_json_if_datetime(value):
    if isinstance(value, datetime.date):
        return value.ctime()
    else:
        return None