import os

from data_models.models import DataFile
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from utils.models import BaseModel

from .create_zip_functions import create_zip

# Create your models here.

status = (
    (0, 'Started'),
    (1, 'Unarchiving'),
    (2, 'Creating bundle'),
    (3, 'Ready'),
    (4, 'Failed'),

)

metadata_type = (
    (0, 'base'),
    (1, 'Camera trap DP'),
    (2, 'COCO'),
)


class DataPackage(BaseModel):
    name = models.CharField(max_length=200)
    data_files = models.ManyToManyField(
        DataFile, related_name="data_bundles")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, related_name="data_bundles",
                              on_delete=models.SET_NULL, null=True)
    status = models.IntegerField(
        choices=status, default=0)
    metadata_type = models.IntegerField(
        choices=metadata_type, default=0)
    includes_files = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def make_zip(self):
        create_zip(self.name, self.data_files,
                   self.metadata_type, self.includes_files)
        self.status = 3
        self.save()

    def clean_data_package(self):
        if self.status == 3:
            try:
                package_path = os.path.join(
                    settings.FILE_STORAGE_ROOT, settings.PACKAGE_PATH)
                os.remove(os.path.join(package_path, self.name+"zip"))
                os.removedirs(package_path)
            except OSError:
                pass


@receiver(pre_delete, sender=DataPackage)
def pre_remove_bundle(sender, instance, **kwargs):
    # deletes the attached file form data storage
    instance.clean_data_package()
