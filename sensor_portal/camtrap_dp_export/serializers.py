import mimetypes
import os

from data_models.models import DataFile
from rest_framework import serializers


class DeploymentSerializerCTDP(serializers.Serializer):
    deploymentID = serializers.CharField(source='deployment_device_ID')
    locationID = serializers.CharField()
    latitude = serializers.DecimalField(
        max_digits=8, decimal_places=6)
    longitude = serializers.DecimalField(
        max_digits=8, decimal_places=6)

    deploymentStart = serializers.DateTimeField(
        source="deployment_start", format="%Y-%m-%dT%H:%M:%S%z")
    deploymentEnd = serializers.DateTimeField(
        source="deployment_start", format="%Y-%m-%dT%H:%M:%S%z")
    setupBy = serializers.CharField()
    cameraID = serializers.CharField()
    cameraModel = serializers.CharField()
    coordinateUncertainty = serializers.FloatField()
    cameraHeight = serializers.FloatField()
    cameraHeading = serializers.IntegerField()
    baitUse = serializers.BooleanField()
    habitatType = serializers.CharField()
    deploymentGroups = serializers.CharField()
    deploymentTags = serializers.CharField()
    deploymentComments = serializers.CharField()


class DataFileSerializerCTDP(serializers.Serializer):
    mediaID = serializers.CharField(source='file_name')
    deploymentID = serializers.CharField()
    captureMethod = serializers.CharField()
    timestamp = serializers.CharField()
    filePath = serializers.CharField()
    fileName = serializers.CharField()
    filePublic = serializers.CharField()
    fileMediatype = serializers.SerializerMethodField()
    favorite = serializers.BooleanField()
    mediaComments = serializers.CharField()

    def get_fileMediatype(self, obj):
        return mimetypes.guess_type(obj.fileName)[0]


class ObservationSerializerCTDP(serializers.Serializer):
    observationID = serializers.CharField()
    deploymentID = serializers.CharField()
    mediaID = serializers.CharField(allow_null=True)
    eventID = serializers.CharField(allow_null=True)
    eventStart = serializers.CharField(allow_null=True)
    eventEnd = serializers.CharField(allow_null=True)
    observationLevel = serializers.CharField()
    observationType = serializers.CharField()
    scientificName = serializers.CharField(allow_null=True)
    count = serializers.IntegerField()
    lifeStage = serializers.CharField(allow_null=True, allow_blank=True)
    sex = serializers.CharField(allow_null=True, allow_blank=True)
    behavior = serializers.CharField(allow_null=True, allow_blank=True)
    individualID = serializers.CharField(allow_null=True)
    bboxX = serializers.FloatField(allow_null=True)
    bboxY = serializers.FloatField(allow_null=True)
    bboxWidth = serializers.FloatField(allow_null=True)
    bboxHeight = serializers.FloatField(allow_null=True)
    classificationMethod = serializers.CharField()
    classifiedBy = serializers.CharField(allow_null=True)
    classificationProbability = serializers.FloatField(allow_null=True)
    observationComments = serializers.CharField(allow_null=True)


class SequenceSerializer(serializers.Serializer):
    eventID = serializers.CharField()
    mediaID = serializers.SerializerMethodField()
    mediaCount = serializers.IntegerField(source='nfiles')
    eventStart = serializers.CharField()
    eventEnd = serializers.CharField()
    mediaID = serializers.SlugRelatedField(
        queryset=DataFile.objects.all(), many=True, source="data_files", slug_field='file_name')
