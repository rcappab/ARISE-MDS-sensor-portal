def data_file_in_deployment(recording_dt, deployment):
    """
    Check if a date falls within a deployment's date range.

    Args:
        recording_dt (datetime): Recording date time to check
        deployment (Deployment): Deployment object to check

    Returns:
        success (boolean), error message (dict where the key is the associated field name)
    """
    if deployment.deployment_end is None:
        deployment_end = ""
    else:
        deployment_end = f" - {str(deployment.deployment_end)}"
    valid_recording_dt_list = deployment.check_dates([recording_dt])
    if all(valid_recording_dt_list):
        return True, ""
    error_message = {"recording_dt": f"recording_dt not in deployment {deployment.deployment_device_ID} date time range "
                     f"{str(deployment.deployment_start)}{deployment_end}"}
    return False, error_message


def deployment_start_time_after_end_time(start_dt, end_dt):
    """
    Check if end time is after start time

    Args:
        start_dt (datetime): Start time to check
        end_dt (datetime): _description_

    Returns:
            tuple: success (boolean), error message (dict where the key is the associated field name)
    """
    if (end_dt is None) or (end_dt > start_dt):
        return True, ""
    error_message = {
        "deployment_end": f"End time {end_dt} must be after start time f{start_dt}"}
    return False, error_message


def deployment_check_overlap(start_dt, end_dt, device, deployment_pk):
    """
    Check if a new deployment of a device would overlap with existing deployments.

    Args:
        start_dt (datetime): start datetime of new deployment
        end_dt (datetime): end datetime of new deployment
        device (Device): Device of new deployment
        deployment_pk (int): pk of a deployment to be ignored when considering overlaps.
        Include if editing an existing deployment to avoid checking for overlap with itself.

    Returns:
            success (boolean), error message (dict where the key is the associated field name)
    """
    overlapping_deployments = device.check_overlap(
        start_dt, end_dt, deployment_pk)
    if len(overlapping_deployments) == 0:
        return True, ""
    error_message = {
        "deployment_start": f"this deployment of {device.device_ID} "
        f"would overlap with {','.join(overlapping_deployments)}"
    }
    return False, error_message


def deployment_check_type(device_type, device):
    """
    Check if a deployment matches it's device type.

    Args:
        device_type (DataType): New deployment device type.
        device (Device): Device of new deployment.

    Returns:
            success (boolean), error message (dict where the key is the associated field name)
    """
    if device_type is None or device.type == device_type:
        return True, ""
    error_message = {
        'device': f"{device.deviceID} is not a {device_type.name} device"}
    return False, error_message


def device_check_type(device_type, device_model):
    """_summary_

    Check if a device matches it's device model type.

    Args:
        device_type (DataType): New device type.
        device_model (DeviceModel): DeviceModel of new device.

    Returns:
            success (boolean), error message (dict where the key is the associated field name)
    """
    if device_type is None or device_model.type == device_type:
        return True, ""
    error_message = {
        'model': f"{device_model.name} is not a {device_type.name} device"}
    return False, error_message


def check_two_keys(primary_key, secondary_key, data, target_model, form_submission=False):
    """
    Function to check if at least one of two keys is included in serialized data.
    If only secondary key is present, get the value of the primary key from the target_model.

    Args:
        primary_key (str): First key to check.
        secondary_key (str): Second key to check.
        data (SerializedData): Serialized data to check for the presence of the keys
        target_model (django.db.models.Model): Model class to pull value of primary key
        form_submission (bool): True if this check is being carried out by a submitted form,
        modifies the error message returned.

    Returns:
            success (boolean)
            error message (dict where the key is the associated field name)
            modified serialized data (SerializedData)
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

    return True, {}, data
