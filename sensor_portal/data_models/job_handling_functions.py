from django.conf import settings
from rest_framework import status

from sensor_portal.celery import app


def register_job(name, task_name, task_data_type, task_admin_only=False, max_items=500, default_args={}):
    def register_job_decorator(func):
        """Register a function as a plug-in"""

        settings.GENERIC_JOBS[task_name] = {"id": len(settings.GENERIC_JOBS.items()),
                                            "name": name,
                                            "task_name": task_name,
                                            "task": func,
                                            "data_type": task_data_type,
                                            "admin_only": task_admin_only,
                                            "max_items": max_items,
                                            "default_args": default_args}
        print(f"Registered generic task {task_name}")
        return func
    return register_job_decorator


def get_job_from_name(job_name, obj_type, obj_pks, job_args, user_pk=None):
    all_args = {f"{obj_type}_pks": obj_pks, **job_args}
    if user_pk is not None:
        all_args["user_pk"] = user_pk
    print(all_args)

    new_task = app.signature(
        job_name, kwargs=all_args, immutable=True)
    return new_task


def start_job_from_name(job_name, obj_type, obj_pks, job_args, user_pk=None):
    from user_management.models import User
    job_dict = settings.GENERIC_JOBS.get(job_name)
    if job_dict is None:
        return False, "Not a registered job", status.HTTP_404_NOT_FOUND

    if user_pk is not None:
        user_obj = User.objects.get(pk=user_pk)
        if job_dict["admin_only"] and not user_obj.is_staff:
            return False, "You are not permited to run this job", status.HTTP_403_FORBIDDEN

        if len(obj_pks) > job_dict["max_items"]:
            return False, "Too many items for this job", status.HTTP_400_BAD_REQUEST

    new_task = get_job_from_name(
        job_name, obj_type, obj_pks, job_args, user_pk)
    new_task.apply_async()
    return True, f"{job_name} started", status.HTTP_200_OK
