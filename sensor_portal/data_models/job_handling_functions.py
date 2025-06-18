from typing import Any, Callable, Dict

from django.conf import settings
from rest_framework import status

from sensor_portal.celery import app


def register_job(
    name: str,
    task_name: str,
    task_data_type: str,
    task_admin_only: bool = False,
    max_items: int = 500,
    default_args: Dict[str, Any] = {}
) -> Callable:
    """
    Decorator to register a function as a plug-in for a generic job.

    Args:
        name (str): The display name of the job.
        task_name (str): The unique identifier for the task.
        task_data_type (str): The type of data the task operates on.
        task_admin_only (bool, optional): Whether the task is restricted to admin users. Defaults to False.
        max_items (int, optional): The maximum number of items the task can process. Defaults to 500.
        default_args (Dict[str, Any], optional): Default arguments for the task. Defaults to an empty dictionary.

    Returns:
        Callable: A decorator function that registers the task.
    """
    def register_job_decorator(func: Callable) -> Callable:
        """Register a function as a plug-in."""
        settings.GENERIC_JOBS[task_name] = {
            "id": len(settings.GENERIC_JOBS.items()),
            "name": name,
            "task_name": task_name,
            "task": func,
            "data_type": task_data_type,
            "admin_only": task_admin_only,
            "max_items": max_items,
            "default_args": default_args,
        }
        print(f"Registered generic task {task_name}")
        return func

    return register_job_decorator


def get_job_from_name(
    job_name: str,
    obj_type: str,
    obj_pks: list[int],
    job_args: dict[str, any],
    user_pk: int | None = None
) -> object:
    """
    Creates a new task signature for a job based on the provided parameters.
    Args:
        job_name (str): The name of the job to be executed.
        obj_type (str): The type of object associated with the job (e.g., "sensor", "device").
        obj_pks (list[int]): A list of primary keys for the objects related to the job.
        job_args (dict[str, any]): Additional arguments required for the job execution.
        user_pk (int | None, optional): The primary key of the user initiating the job. Defaults to None.
    Returns:
        object: A Celery task signature object representing the job.
    """
    all_args = {f"{obj_type}_pks": obj_pks, **job_args}
    if user_pk is not None:
        all_args["user_pk"] = user_pk
    print(job_args)

    new_task = app.signature(
        job_name, kwargs=all_args, immutable=True)
    return new_task


def start_job_from_name(
    job_name: str,
    obj_type: str,
    obj_pks: list[int],
    job_args: dict[str, Any],
    user_pk: int | None = None
) -> tuple[bool, str, int]:
    """
    Starts a job based on the provided parameters.

    Args:
        job_name (str): The name of the job to be executed.
        obj_type (str): The type of object associated with the job (e.g., "sensor", "device").
        obj_pks (list[int]): A list of primary keys for the objects related to the job.
        job_args (dict[str, Any]): Additional arguments required for the job execution.
        user_pk (int | None, optional): The primary key of the user initiating the job. Defaults to None.

    Returns:
        tuple[bool, str, int]: A tuple containing:
            - A boolean indicating success or failure.
            - A message describing the result.
            - An HTTP status code.
    """
    from user_management.models import User

    job_dict = settings.GENERIC_JOBS.get(job_name)
    if job_dict is None:
        return False, "Not a registered job", status.HTTP_404_NOT_FOUND

    if user_pk is not None:
        user_obj = User.objects.get(pk=user_pk)
        if job_dict["admin_only"] and not user_obj.is_staff:
            return False, "You are not permitted to run this job", status.HTTP_403_FORBIDDEN

        if len(obj_pks) > job_dict["max_items"]:
            return False, "Too many items for this job", status.HTTP_400_BAD_REQUEST

    new_task = get_job_from_name(
        job_name, obj_type, obj_pks, job_args, user_pk
    )
    new_task.apply_async()
    return True, f"{job_name} started", status.HTTP_200_OK
