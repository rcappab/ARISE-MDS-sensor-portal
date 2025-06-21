
from rest_framework import serializers
from utils.serializers import CreatedModifiedMixIn, OwnerMixIn

from .models import DataPackage


class DataPackageSerializer(OwnerMixIn, CreatedModifiedMixIn):

    status_id = serializers.IntegerField(source="status", write_only=True)
    status = serializers.CharField(
        source="get_status_display", read_only=True, help_text="Current status of this data package.")
    medatatype_id = serializers.IntegerField(
        source="metadatatype", write_only=True, help_text="Type of metadata ID, e.g. 0 for default, 1 for camtrap dp.")
    metadatatype = serializers.CharField(
        source="get_metadata_display", read_only=True, help_text="Type of metadata , e.g. default, camtrap dp etc.")

    class Meta:
        model = DataPackage
        exclude = ["data_files"]
