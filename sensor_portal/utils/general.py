from django.conf import settings
import pytz
import dateutil.parser
import os
import datetime

from django.core.exceptions import ObjectDoesNotExist
import traceback


def get_global_project():
    from data_models.models import Project
    try:
        global_project = Project.objects.get(
            project_ID=settings.GLOBAL_PROJECT_ID)
        return global_project
    except ObjectDoesNotExist:
        global_project = Project(project_ID=settings.GLOBAL_PROJECT_ID,
                                 name=settings.GLOBAL_PROJECT_ID,
                                 objectives="Global project for all deployments")
        global_project.save()
        return global_project
    except:
        print(" Error: " + traceback.format_exc())
        pass


def check_dt(dt, device_timezone=None):
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
