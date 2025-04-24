from sensor_portal.celery import app


def get_job_from_name(job_name, user_pk, file_pks, job_args):
    all_args = {"file_pks": file_pks, **job_args}
    if user_pk is not None:
        all_args["user_pk"] = user_pk
    print(all_args)
    new_task = app.signature(
        job_name, kwargs=all_args, immutable=True)
    return new_task


def start_job_from_name(job_name, user_pk, file_pks, job_args):
    new_task = get_job_from_name(job_name, user_pk, file_pks, job_args)
    new_task.apply_async()
