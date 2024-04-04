from django.conf import settings
import pytz
import dateutil.parser


def check_dt(dt, device_timezone = None):
    if dt is None:
        return dt

    if device_timezone is None:
        device_timezone = settings.TIME_ZONE
    if type(dt) is str:
        dt = dateutil.parser.parse(dt)

    if dt.tzinfo is None:
        mytz = pytz.timezone(device_timezone)
        dt = mytz.localize(dt)

    return dt
