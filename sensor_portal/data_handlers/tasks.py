from celery import shared_task


@shared_task(name="data_handler_generate_thumbnails")
def generate_thumbnails(file_pks):
    from .post_upload_task_handler import post_upload_task_handler
    from .functions import generate_thumbnail
    post_upload_task_handler(file_pks, generate_thumbnail)
