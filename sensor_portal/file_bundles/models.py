from data_models.models import DataFile
from django.conf import settings
from django.db import models
from utils.models import BaseModel

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


class FileBundle(BaseModel):
    name = models.CharField(max_length=200)
    data_files = models.ManyToManyField(
        DataFile, related_name="data_bundles")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, related_name="data_bundles",
                              on_delete=models.SET_NULL, null=True)
    status = models.IntegerField(
        choices=status, default=0)

    def __str__(self):
        return self.name
