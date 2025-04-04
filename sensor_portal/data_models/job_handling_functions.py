from sensor_portal.celery import app


def start_job_from_name(job_name, user_pk, file_pks, job_args):
    all_args = {"file_pks": file_pks, "user_pk": user_pk, **job_args}
    print(all_args)
    new_task = app.signature(
        job_name, kwargs=all_args, immutable=True)
    new_task.apply_async()
