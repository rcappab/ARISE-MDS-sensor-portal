
from rest_framework import serializers
from utils.serializers import CreatedModifiedMixIn, OwnerMixIn

from .models import DataPackage


class DataPackageSerializer(OwnerMixIn, CreatedModifiedMixIn):

    status_id = serializers.IntegerField(source="status", write_only=True)
    status = serializers.CharField(
        source="get_status_display", read_only=True)
    medatatype_id = serializers.IntegerField(
        source="metadatatype", write_only=True)
    metadatatype = serializers.CharField(
        source="get_metadata_display", read_only=True)

    class Meta:
        model = DataPackage
        exclude = ["data_files"]
