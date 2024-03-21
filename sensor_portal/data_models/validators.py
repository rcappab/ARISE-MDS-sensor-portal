from .models import *


def data_file_in_deployment(recording_dt, deployment):
    if deployment.deploymentEnd is None:
        deployment_end = ""
    else:
        deployment_end = f" - {str(deployment.deploymentEnd)}"
    valid_recording_dt_list = deployment.check_dates([recording_dt])
    if not len(valid_recording_dt_list) == 0:
        return True, ""
    error_message = f"recording_dt not in deployment {deployment.deployment_deviceID} date time range " \
                    f"{str(deployment.deploymentStart)}{deployment_end}"
    return False, error_message


def deployment_start_time_after_end_time(start_dt, end_dt):
    if (end_dt is None) or (end_dt > start_dt):
        return True, ""
    error_message = f"End time {end_dt} must be after start time f{start_dt}"
    return False, error_message


def deployment_check_overlap(start_dt, end_dt, device):
    overlapping_deployments = device.check_overlap(start_dt, end_dt)
    if len(overlapping_deployments) == 0:
        return True, ""
    error_message = f"this deployment of {device.deviceID} would overlap with {','.join(overlapping_deployments)}"
    return False, error_message


def deployment_check_type(device_type, device):
    if device_type is None or device.type == device_type:
        return True, ""
    error_message = f"{device.deviceID} is not a {device_type.name} device"
    return False, error_message


