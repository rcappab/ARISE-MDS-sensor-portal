from celery import shared_task
from base_data_handler_class import post_upload_task_handler


@shared_task(name="generate_thumbnails")
def generate_thumbnails(file_pks):
    from .functions import generate_thumbnail
    post_upload_task_handler(file_pks, generate_thumbnail)
