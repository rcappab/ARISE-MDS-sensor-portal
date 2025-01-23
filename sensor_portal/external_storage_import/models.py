from django.db import models
from django.conf import settings
from utils.models import BaseModel
from encrypted_model_fields.fields import EncryptedCharField


class DataStorageInput(BaseModel):
    name = models.CharField(max_length=20, unique=True)
    username = models.CharField(
        max_length=50, unique=True)
    password = EncryptedCharField(max_length=128)
    address = models.CharField(
        max_length=100, unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, related_name="owned_inputstorages",
                              on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name
