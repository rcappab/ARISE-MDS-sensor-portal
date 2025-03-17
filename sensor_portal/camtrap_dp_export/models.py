# from data_models.models import DataFile
# from django.conf import settings
# from django.db import models
# from utils.models import BaseModel

# # Create your models here.


# class FileBundle(BaseModel):
#     name = models.CharField(max_length=200)
#     data_files = models.ManyToManyField(
#         DataFile, related_name="data_bundles")
#     owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, related_name="data_bundles",
#                               on_delete=models.SET_NULL, null=True)

#     def __str__(self):
#         return self.name
