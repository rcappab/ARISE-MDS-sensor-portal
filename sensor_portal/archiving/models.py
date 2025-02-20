import os

from django.conf import settings
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone as djtimezone
from encrypted_model_fields.fields import EncryptedCharField
from utils.models import BaseModel
from utils.ssh_client import SSH_client


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

    def clean_tar(self, delete_obj=False):
        if self.local_storage:
            tar_name = self.name
            if ".tar.gz" not in tar_name:
                tar_name = tar_name+".tar.gz"
            try:
                os.remove(os.path.join(
                    settings.FILE_STORAGE_ROOT, self.path, tar_name))
                os.removedirs(os.path.join(
                    settings.FILE_STORAGE_ROOT, self.path))
            except OSError as e:
                print(repr(e))

            if not delete_obj:
                self.local_storage = False
                self.save()


@receiver(pre_delete, sender=TarFile)
def pre_remove_tar(sender, instance, **kwargs):
    # deletes the attached file form data storage
    instance.clean_tar(True)
