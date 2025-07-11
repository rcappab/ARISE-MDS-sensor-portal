import logging
from datetime import datetime, timedelta
from typing import List

from bridgekeeper import perms
from celery import shared_task
from data_models.job_handling_functions import register_job
from django.contrib.sites.models import Site
from django.db.models import (BooleanField, DurationField, ExpressionWrapper,
                              F, IntegerField, Max, Q)
from django.db.models.functions import ExtractHour
from django.utils import timezone
from user_management.models import User
from utils.email import send_email_to_user

from sensor_portal.celery import app

from .models import DataFile, Deployment, Device, Project

logger = logging.getLogger(__name__)


@app.task(name="flag_humans")
@register_job("Change human flag", "flag_humans", "datafile", True,
              default_args={"has_human": False})
def flag_humans(datafile_pks: List[int], has_human: bool = False, **kwargs):
    """
    Set the has_human flag on data files.
    Args:
        datafile_pks (List[int]): List of data file primary keys to update.
        has_human (bool, optional): Value to set the flag to. Defaults to False.
    """
    file_objs = DataFile.objects.filter(
        pk__in=datafile_pks)
    logger.info(file_objs.count())
    file_objs.update(has_human=has_human)


@app.task()
def clean_all_files():
    """
    Remove files that are archived and have not been modified in the projects clean time.
    """
    projects_to_clean = Project.objects.filter(archive__isnull=False)
    logger.info(f"Found {projects_to_clean.count()} projects to clean.")
    for project in projects_to_clean:
        clean_time = project.clean_time
        logger.info(
            f"Cleaning project: {project.name} with clean time: {clean_time} days.")
        files_to_clean = DataFile.objects.filter(
            local_storage=True,
            archived=True,
            do_not_remove=False,
            favourite_of__isnull=True,
            deployment_last_image__isnull=True)

        files_to_clean = files_to_clean.annotate(file_age=ExpressionWrapper(
            timezone.now().date() - F('modified_on__date'), output_field=DurationField()))
        files_to_clean = files_to_clean.filter(
            file_age__gt=timedelta(days=clean_time))
        logger.info(
            f"Found {files_to_clean.count()} files to clean for project: {project.name}.")
        for file in files_to_clean:
            try:
                logger.info(f"Cleaning file: {file.file_name} (ID: {file.pk})")
                file.clean_file()
            except Exception as e:
                logger.info(
                    f"Error cleaning file {file.file_name} (ID: {file.pk}): {e}")


@app.task()
def check_deployment_active():
    """
    Check if a deployment is active or not
    """
    # Get all deployments that are inactive that should be active
    make_active = Deployment.objects.filter(
        is_active=False,
        deployment_start__lte=timezone.now(),
    ).filter(Q(deployment_end__isnull=True) | Q(deployment_end__gte=timezone.now()))

    make_active.update(is_active=True, modified_on=timezone.now())

    # Get all deployments that are active that should be inactive
    make_inactive = Deployment.objects.filter(
        is_active=True,
    ).filter(Q(deployment_start__gte=timezone.now()) | Q(deployment_end__lte=timezone.now()))

    make_inactive.update(is_active=False, modified_on=timezone.now())


@app.task()
def check_device_status():
    """
    Check if device has transmitted in the allotted time and email managers
    """
    logger.info("Checking device status...")

    auto_devices = Device.objects.filter(
        deployments__is_active=True,
        autoupdate=True,
    )

    bad_devices_pks = []
    bad_devices_values = []
    for device in auto_devices:
        # get the last file time for each device
        last_file_time = device.deployments.filter(is_active=True).aggregate(
            Max('files__recording_dt')).get('files__recording_dt__max')
        if last_file_time is None:
            logger.info(f"Device {device.device_ID} has no files.")
            bad_devices_pks.append(device.pk)
            bad_devices_values.append({
                'device_ID': device.device_ID,
                'name': device.name,
                'file_hours': None
            })
            continue
        # calculate the age of the last file
        file_age = timezone.now() - last_file_time
        # check if the file age is greater than the update time
        if file_age > timedelta(hours=device.update_time):
            logger.info(
                f"Device {device.device_ID} has not transmitted in the allotted time: {file_age.total_seconds() / 3600} hours.")
            # add the device to the list of bad devices
            bad_devices_pks.append(device.pk)
            bad_devices_values.append({
                'device_ID': device.device_ID,
                'name': device.name,
                'file_hours': file_age.total_seconds() / 3600  # convert to hours
            })

    bad_devices = Device.objects.filter(pk__in=bad_devices_pks)

    # get all unique managers
    all_bad_device_users = User.objects.filter(
        deviceuser__isnull=True).filter(
            Q(owned_projects__deployments__device__in=bad_devices) |
        Q(managed_projects__deployments__device__in=bad_devices) |
        Q(owned_devices__in=bad_devices) |
        Q(managed_devices__in=bad_devices) |
        Q(owned_deployments__device__in=bad_devices)
    ).distinct()

    for user in all_bad_device_users:
        # for each manager, get their bad devices
        users_bad_devices = perms['data_models.change_device'].filter(
            user, bad_devices_values).distinct()

        if not users_bad_devices.exists():
            continue

        device_list = [
            f'{x.get("device_ID")} - {x.get("name")} - {x.get("file_hours")}' for x in users_bad_devices]
        device_list_string = " \n".join(device_list)

        # send them an email
        email_body = f"""
        Dear {user.first_name} {user.last_name},\n
        \n
        The following devices which you manage have not transmitted in their alloted time: \n
        {device_list_string}
        """

        send_email_to_user(
            user,
            subject=f"{Site.objects.get_current().name} - {users_bad_devices.count()} devices have not transmitted in alloted time",
            body=email_body)
