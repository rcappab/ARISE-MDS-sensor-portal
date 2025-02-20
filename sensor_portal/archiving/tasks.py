
import os
from posixpath import join as posixjoin

from celery import chord, group, shared_task
from data_models.models import DataFile, TarFile
from django.conf import settings
from utils.general import divide_chunks
from utils.task_functions import TooManyTasks, check_simultaneous_tasks

from .exceptions import TAROffline
from .models import Archive
from .tar_functions import check_tar_status, create_tar_files


@shared_task
def check_all_archive_projects_task():
    all_archives = Archive.objects.all()
    for archive in all_archives:
        archive.check_projects()


@shared_task
def check_all_uploads_task():
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


@shared_task
def get_files_from_archive_task(file_pks, callback=None):
    file_objs = DataFile.objects.filter(pk__in=file_pks)

    # Get unique TAR files
    tar_file_pks = list(TarFile.objects.filter(
        pk__in=file_objs.values_list('tar_file__pk').distinct()))

    all_tasks = []
    # For each TAR create job to retrieve files
    for tar_file_pk in tar_file_pks:
        target_file_pks = list(file_objs.filter(tar_file__pk=tar_file_pk))
        all_tasks.append(get_files_from_archived_tar_task.si(
            tar_file_pk, target_file_pks))

    task_group = group(all_tasks)
    if callback is not None:
        task_group = chord(task_group, callback)
    task_group.apply_async()


@shared_task(autoretry_for=(TooManyTasks, TAROffline),
             max_retries=None,
             retry_backoff=2*60,
             retry_backoff_max=5 * 60,
             retry_jitter=True)
def get_files_from_archived_tar_task(self, tar_file_pk, target_file_pks):

    check_simultaneous_tasks()

    tar_file_obj = TarFile.objects.get(pk=tar_file_pk)
    file_objs = DataFile.objects.filter(pk__in=target_file_pks)
    file_names = file_objs.full_names()
    # Connect to archive
    archive_obj = tar_file_obj.archive
    ssh_client = archive_obj.init_ssh_client()

    # Find target TAR file
    tar_name = tar_file_obj.name+'.tar.gz'
    tar_path = posixjoin(tar_file_obj.path, tar_name)
    status_code, stdout, stderr = ssh_client.send_ssh_command(
        f"dmls -l {tar_path}")

    status_code, target_tar_status = check_tar_status(ssh_client, tar_path)
    print(
        f"{tar_path}: Get TAR status {status_code}")

    if status_code == 1:
        tar_name = tar_file_obj.name
        tar_path = posixjoin(tar_file_obj.path, tar_name)
        status_code, target_tar_status = check_tar_status(ssh_client, tar_path)
        print(
            f"{tar_path}: Get TAR status  {status_code}")
        if status_code == 1:
            raise Exception(f"{tar_path}: TAR file not present at this path")

    print(
        f"{tar_path}: Get TAR status {status_code} {target_tar_status}")

    online_statuses = ['(REG)', '(DUL)', '(MIG)']
    if target_tar_status not in online_statuses:
        initial_offline = True
        print(f"{tar_path}: Offline")
        if target_tar_status != '(UNM)':
            status_code, stdout, stderr = ssh_client.send_ssh_command(
                f"dmget {tar_path}")
            print(
                f"{tar_path}: Get TAR from tape {status_code} {stdout}")

            status_code, target_tar_status = check_tar_status(
                ssh_client, tar_path)
        else:
            # TAR is already unmigrating
            raise (TAROffline(f"{tar_path}: already unmigrating"))

        if target_tar_status not in online_statuses:
            # This shouldn't happen.
            raise Exception(f"{tar_path}: TAR file could not be staged")

    else:
        initial_offline = False

    status_code, stdout, stderr = ssh_client.send_ssh_command(
        f"tar tvf {tar_path}", return_strings=False)

    print(f"{tar_path}: List TAR files")

    in_tar_file_paths = []
    in_tar_found_files = []
    for file_line in stdout:
        # extract the tar output line's filepath
        split_file_line = file_line.split(" ")
        line_file_path = split_file_line[-1].replace("\n", "")
        found_file_paths = [x for x in file_names if x in line_file_path]
        if len(found_file_paths) > 0:
            # If this file is one of our target file, save the in-tar path
            in_tar_file_paths.append(line_file_path)
            in_tar_found_files.append(found_file_paths[0])
            print(f"{tar_path}: {len(in_tar_file_paths)}/{len(file_names)}")

        if len(in_tar_file_paths) == len(file_names):
            # If we have found all our target_files
            print(f"{tar_path}: All files_found")
            break

    if len(in_tar_file_paths) == 0:
        raise Exception(f"{tar_path}: No files found in TAR")
    else:
        missing_files = [x for x in file_names if x not in in_tar_found_files]
        if missing_files > 0:
            print(f"{tar_path}: Files not found: {missing_files}")

    temp_path = posixjoin(tar_file_obj.path, "temp", self.id)
    ssh_client.mkdir_p(temp_path, is_dir=True)

    chunked_in_tar_file_paths = [
        x for x in divide_chunks(in_tar_file_paths, 500)]
    for idx, in_tar_file_paths_set in enumerate(chunked_in_tar_file_paths):
        print(f"{tar_path}: Extract file chunk {idx}/{len(chunked_in_tar_file_paths)}")
        combined_in_tar_file_paths = (
            " ".join([f"'{x}'" for x in in_tar_file_paths_set]))
        status_code, stdout, stderr = ssh_client.send_ssh_command(
            f"tar -zxvf {tar_path} -C {temp_path} {combined_in_tar_file_paths}"
        )
        print(
            f"{tar_path}: Extract file chunk {idx}/{len(chunked_in_tar_file_paths)} {status_code}")

    ssh_client.connect_to_scp()
    file_objs_to_update = []
    for idx, in_tar_file_path in enumerate(in_tar_file_paths):
        try:
            full_file_name = os.path.split(in_tar_file_path)[1]
            file_name = os.path.splitext(full_file_name)[0]

            # get file object
            file_obj = file_objs.get(file_name=file_name)
            local_dir = os.path.join(settings.FILE_STORAGE_ROOT, file_obj.path)
            os.makedirs(local_dir, exist_ok=True)
            local_file_path = os.path.join(local_dir, full_file_name)

            temp_file_path = posixjoin(temp_path, in_tar_file_path)
            if not os.path.exists(local_file_path):
                ssh_client.scp_c.get(
                    temp_file_path, local_file_path, preserve_times=True)

            file_obj.local_path = settings.FILE_STORAGE_ROOT
            file_obj.local_storage = True
            file_objs_to_update.append(file_obj)
        except Exception as e:
            print(f"{tar_path}: Error retrieving file: {repr(e)}")
    print(f"{tar_path}: Update database")
    DataFile.objects.bulk_update(file_objs_to_update)
    print(f"{tar_path}: Clear temporary files")
    status_code, stdout, stderr = ssh_client.send_ssh_command(
        f"rm - rf {temp_path}")
