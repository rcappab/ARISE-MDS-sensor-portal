import logging
import os
from posixpath import join as posixjoin

from django.conf import settings
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone as djtimezone
from encrypted_model_fields.fields import EncryptedCharField
from utils.general import try_remove_file_clean_dirs
from utils.models import BaseModel
from utils.ssh_client import SSH_client

logger = logging.getLogger(__name__)


class Archive(BaseModel):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    username = models.CharField(
        max_length=50, unique=True)
    password = EncryptedCharField(max_length=128)
    address = models.CharField(
        max_length=100, unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, related_name="owned_archives",
                              on_delete=models.SET_NULL, null=True)

    root_folder = models.CharField(
        max_length=100, unique=True)

    def init_ssh_client(self) -> SSH_client:
        return SSH_client(self.username, self.password, self.address, 22)

    def check_projects(self):
        from .functions import check_archive_projects
        check_archive_projects(self)

    def check_upload(self):
        from .functions import check_archive_upload
        check_archive_upload(self)


class TarFile(BaseModel):
    name = models.CharField(max_length=200)
    archived_dt = models.DateTimeField(default=djtimezone.now)

    uploading = models.BooleanField(default=False)

    local_storage = models.BooleanField(default=True)
    archived = models.BooleanField(default=False)
    path = models.CharField(max_length=500, blank=True)
    archive = models.ForeignKey(
        Archive, related_name="tar_files", on_delete=models.PROTECT, null=True)

    def __str__(self):
        return self.name

    def clean_tar(self, delete_obj: bool = False, force_delete=False) -> bool:
        logger.info(
            f"Clean TAR file {self.name} - Delete object: {delete_obj}")
        if not self.local_storage and not self.archived and not self.uploading:
            logger.info(
                f"Clean TAR file {self.name} - object exists only in database")
            return True
        if self.local_storage:
            tar_name = self.name
            if ".tar.gz" not in tar_name:
                tar_name = tar_name+".tar.gz"
            tar_path = os.path.join(
                settings.FILE_STORAGE_ROOT, self.path, tar_name)
            logger.info(
                f"Clean TAR file {self.name} - try to delete local TAR")

            success = try_remove_file_clean_dirs(tar_path)

            if not success and not force_delete:
                logger.error(
                    f"Clean TAR file {self.name} - failed - could not delete local TAR")
                return False
            elif success:
                logger.info(
                    f"Clean TAR file {self.name} - try to delete local TAR - success")

            if not delete_obj:
                logger.info(
                    f"Clean TAR file {self.name} - Alter database object")
                self.local_storage = False
                self.save()

            return True

        elif not self.local_storage and delete_obj and force_delete:
            if not all(self.files.values_list("local_storage", flat=True)):
                logger.error(f"{self.name}: Some files contained in this TAR are no longer stored locally.\
                              The remote TAR cannot be deleted.")
                return False
                # deletes the attached file form data storage
            self.files.all().update(archived=False)
            ssh_client = self.archive.init_ssh_client()
            ssh_connect_success = ssh_client.connect_to_ssh()
            if not ssh_connect_success:
                return
            remote_path = posixjoin(self.path, self.name+".tar.gz")
            status_code, stdout, stderr = ssh_client.send_ssh_command(
                f"rm {remote_path}")
            if status_code != 0:
                remote_path = posixjoin(self.path, self.name)
                status_code, stdout, stderr = ssh_client.send_ssh_command(
                    f"rm {remote_path}")
            if status_code != 0:
                logger.info(
                    f"{self.name}: Cannot remove remote TAR. {stdout}")
                return False

            else:

                logger.info(f"{self.name}: Remote TAR removed.")
                status_code, stdout, stderr = ssh_client.send_ssh_command(
                    f"find {self.path} -type d -empty -delete")
                return True
        else:
            return False


@receiver(pre_delete, sender=TarFile)
def pre_remove_tar(sender, instance: TarFile, **kwargs):
    success = instance.clean_tar(True)
    if not success:
        raise (Exception(f"Unable to remove TAR file {instance.name}"))
