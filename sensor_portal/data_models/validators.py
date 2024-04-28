from .models import *


def data_file_in_deployment(recording_dt, deployment):
    """_summary_

    Args:
        recording_dt (_type_): _description_
        deployment (_type_): _description_

    Returns:
        _type_: _description_
    """
    if deployment.deploymentEnd is None:
        deployment_end = ""
    else:
        deployment_end = f" - {str(deployment.deploymentEnd)}"
    valid_recording_dt_list = deployment.check_dates([recording_dt])
    if not len(valid_recording_dt_list) == 0:
        return True, ""
    error_message = {"recording_dt": f"recording_dt not in deployment {deployment.deployment_deviceID} date time range "
                     f"{str(deployment.deploymentStart)}{deployment_end}"}
    return False, error_message


def deployment_start_time_after_end_time(start_dt, end_dt):
    """_summary_

    Args:
        start_dt (_type_): _description_
        end_dt (_type_): _description_

    Returns:
        _type_: _description_
    """
    if (end_dt is None) or (end_dt > start_dt):
        return True, ""
    error_message = {
        "deploymentEnd": f"End time {end_dt} must be after start time f{start_dt}"}
    return False, error_message


def deployment_check_overlap(start_dt, end_dt, device, deployment_pk):
    """_summary_

    Args:
        start_dt (_type_): _description_
        end_dt (_type_): _description_
        device (_type_): _description_
        deployment_pk (_type_): _description_

    Returns:
        _type_: _description_
    """
    overlapping_deployments = device.check_overlap(
        start_dt, end_dt, deployment_pk)
    if len(overlapping_deployments) == 0:
        return True, ""
    error_message = {"deploymentStart": f"this deployment of {device.deviceID} would overlap with {','.join(overlapping_deployments)}",
                     "deploymentEnd": f"this deployment of {device.deviceID} would overlap with {','.join(overlapping_deployments)}"}
    return False, error_message


def deployment_check_type(device_type, device):
    """_summary_

    Args:
        device_type (_type_): _description_
        device (_type_): _description_

    Returns:
        _type_: _description_
    """
    if device_type is None or device.type == device_type:
        return True, ""
    error_message = {
        'device': f"{device.deviceID} is not a {device_type.name} device"}
    return False, error_message


def check_two_keys(primary_key, secondary_key, data, target_model, form_submission=False):
    """_summary_

    Args:
        primary_key (_type_): _description_
        secondary_key (_type_): _description_
        data (_type_): _description_
        target_model (_type_): _description_

    Returns:
        _type_: _description_
    """

    if data.get(primary_key) is None and data.get(secondary_key) is None:
        if form_submission:
            message = {primary_key: f"{primary_key} is required."}
        else:
            message = {primary_key: f"Either {primary_key} or {secondary_key} are required.",
                       secondary_key: f"Either {primary_key} or {secondary_key} are required."}
        return False, message, data
    elif data.get(primary_key) is None:
        data[primary_key] = target_model.objects.get(
            pk=data.get(secondary_key))

    return True, "", data
