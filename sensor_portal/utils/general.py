import datetime
import os
from datetime import datetime as dt

import dateutil.parser
import pytz
from django.conf import settings
from PIL import ExifTags, Image


def check_dt(dt, device_timezone=None, localise=True):
    if dt is None:
        return dt

    if device_timezone is None:
        device_timezone = settings.TIME_ZONE

    if type(dt) is str:
        dt = dateutil.parser.parse(dt, dayfirst=False, yearfirst=True)

    if dt.tzinfo is None and localise:
        mytz = pytz.timezone(device_timezone)
        dt = mytz.localize(dt)

    return dt


def get_new_name(deployment, recording_dt, file_local_path, file_path, file_n=None):
    if file_n is None:
        file_n = get_n_files(os.path.join(file_local_path, file_path)) + 1
    newname = f"{deployment.deployment_deviceID}_{datetime.strftime(recording_dt, '%Y-%m-%d_%H-%M-%S')}_" \
              f"({file_n})"
    return newname


def get_n_files(dir_path):
    if os.path.exists(dir_path):
        all_files = os.listdir(dir_path)
        # only with extension
        all_files = [x for x in all_files if '.' in x]
        n_files = len(all_files)
    else:
        n_files = 0
    return n_files


def handle_uploaded_file(file, filepath, multipart=False):
    os.makedirs(os.path.split(filepath)[0], exist_ok=True)
    if multipart and os.path.exists(filepath):
        print("append to file")
        with open(filepath, 'ab+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
    else:
        with open(filepath, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)


def clear_uploaded_file(filepath):
    try:
        os.remove(filepath)
    except OSError:
        pass


def get_image_recording_dt(uploaded_file):
    si = uploaded_file.file
    image = Image.open(si)
    exif = image.getexif()
    exif_tags = {ExifTags.TAGS[k]: v for k,
                 v in exif.items() if k in ExifTags.TAGS}
    recording_dt = exif_tags.get('DateTimeOriginal')
    if recording_dt is None:
        recording_dt = exif_tags.get('DateTime')
    if recording_dt is None:
        return None
    return dt.strptime(recording_dt, '%Y:%m:%d %H:%M:%S')
