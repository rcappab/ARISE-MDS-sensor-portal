from celery import shared_task

from .models import Archive
from .tar_functions import create_tar_files


@shared_task
def check_all_archive_projects_task():
    all_archives = Archive.objects.all()
    for archive in all_archives:
        archive.check_projects()


@shared_task
def check_all_archive_projects_task():
    all_archives = Archive.objects.all()
    for archive in all_archives:
        archive.check_upload()


@shared_task
def create_tar_files_task(file_pks: list[int], archive_pk: int):
    """
    Task wrapper for create_tar_files function.

    Args:
        file_pks (list[int]): pks of files to be TARred
        archive_pk (int): pk of archive to which these TARs will be attached
    """
    create_tar_files(file_pks, archive_pk)


@shared_task
def check_archive_upload_task(archive_pk: int):
    archive = Archive.objects.get(pk=archive_pk)
    archive.check_upload()
