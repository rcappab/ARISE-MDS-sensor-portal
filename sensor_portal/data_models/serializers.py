from rest_framework_gis import serializers as geoserializers
from rest_framework import serializers
from .models import *
import magic
from PIL import Image, ExifTags


class OwnerMangerMixIn(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    managers = serializers.StringRelatedField(many=True)

    def create(self, validated_data):
        if self.context['request'].user:
            validated_data['owner'] = self.context['request'].user
        return super(OwnerMangerMixIn, self).create(validated_data)

    def to_representation(self, instance):
        initial_rep = super(OwnerMangerMixIn, self).to_representation(instance)
        fields_to_pop = [
            "owner",
            "managers",
        ]
        user_is_manager = self.context['request'].user.has_perm(self.management_perm, obj=instance)
        if not user_is_manager:
            [initial_rep.pop(field, '') for field in fields_to_pop]
        return initial_rep


class DeploymentFieldsMixIn(OwnerMangerMixIn, serializers.ModelSerializer):
    device_type = serializers.StringRelatedField()
    device = serializers.StringRelatedField()
    device_id = serializers.PrimaryKeyRelatedField(read_only=True)
    project = serializers.StringRelatedField(many=True)
    project_ids = serializers.PrimaryKeyRelatedField(source="project", read_only=True, many=True)
    site = serializers.StringRelatedField()
    site_id = serializers.PrimaryKeyRelatedField(read_only=True)

    # check project permissions here or in viewpoint

    class Meta:
        model = Deployment
        exclude = ['last_image', 'last_file']

    def __init__(self, *args, **kwargs):
        self.management_perm = 'data_models.change_deployment'
        super(DeploymentFieldsMixIn, self).__init__(*args, **kwargs)


class DeploymentSerializer(DeploymentFieldsMixIn, serializers.ModelSerializer):
    pass


class DeploymentSerializer_GeoJSON(DeploymentFieldsMixIn, geoserializers.GeoFeatureModelSerializer):
    def __init__(self, *args, **kwargs):
        self.Meta.geo_field = "point"
        super(DeploymentFieldsMixIn, self).__init__(*args, **kwargs)


class ProjectSerializer(OwnerMangerMixIn, serializers.ModelSerializer):
    class Meta:
        model = Project
        exclude = []

    def __init__(self, *args, **kwargs):
        self.management_perm = 'data_models.change_project'
        super(ProjectSerializer, self).__init__(*args, **kwargs)


class DeviceSerializer(OwnerMangerMixIn, serializers.ModelSerializer):
    device_type = serializers.StringRelatedField()
    username = serializers.CharField()
    authentication = serializers.CharField()

    class Meta:
        model = Device
        exclude = []

    def __init__(self, *args, **kwargs):
        self.management_perm = 'data_models.change_device'
        super(DeviceSerializer, self).__init__(*args, **kwargs)

    def to_representation(self, instance):
        initial_rep = super(DeviceSerializer, self).to_representation(instance)
        fields_to_pop = [
            "username",
            "authentication",
        ]
        user_is_manager = self.context['request'].user.has_perm(self.management_perm, obj=instance)
        print(user_is_manager)
        if not user_is_manager:
            [initial_rep.pop(field, '') for field in fields_to_pop]
        return initial_rep


class DataFileSerializer(serializers.ModelSerializer):
    deployment = serializers.StringRelatedField()
    deployment_id = serializers.PrimaryKeyRelatedField(read_only=True)
    file_type = serializers.StringRelatedField()

    class Meta:
        model = DataFile
        exclude = ["do_not_remove"]


class DataFileUploadSerializer(serializers.Serializer):
    deployment = serializers.CharField(required=False)
    device = serializers.CharField(required=False)
    files = serializers.ListField(child=serializers.FileField(allow_empty_file=False, max_length=None))
    extra_info = serializers.JSONField(required=False)
    recording_dt = serializers.ListField(child=serializers.DateTimeField(), required=False)
    autoupdate = serializers.BooleanField(default=False)
    rename = serializers.BooleanField(default=True)
    check_filename = serializers.BooleanField(default=True)
    data_types = serializers.ListField(child = serializers.StringRelatedField(), required=False)

    def create(self, validated_data):
        return validated_data

    def validate(self, data):
        data = super().validate(data)

        #  Check a deployment or device is supplied
        if data.get('deployment') is None and data.get('device') is None:
            raise serializers.ValidationError("A deployment or a device must be supplied")

        #  if not an image, user must supply the recording date time
        files = data.get("files")
        is_not_image = ["image" not in magic.from_buffer(x.read(), mime=True) for x in files]
        if any(is_not_image):
            raise serializers.ValidationError("Recording date times can only be extracted from images, "
                                              "please provide 'recording_dt' or upload only images")

        #  check recording_dt and number of files match
        if data.get('recording_dt') is not None:
            recording_dt = data.get('recording_dt')
            if len(recording_dt) > 1 & len(recording_dt) != len(data.get('files')):
                raise serializers.ValidationError("More than one recording_dt was supplied, "
                                                  "but the number does not match the number of files")

        if data.get('recording_dt') is None:
            data['recording_dt'] = [get_image_recording_dt(x) for x in files]

        return data

    def update(self, validated_data):
        # Not used
        pass

    def save(self):
        print("during save")
        print(self.validated_data)


def get_image_recording_dt(uploaded_file):
    si = uploaded_file.file
    image = Image.open(si)
    exif = image.getexif()
    exif_tags = {ExifTags.TAGS[k]: v for k, v in exif.items() if k in ExifTags.TAGS}
    recording_dt = exif_tags.get('DateTimeOriginal')
    if recording_dt is None:
        recording_dt = exif_tags.get('DateTime')
    if recording_dt is None:
        raise serializers.ValidationError(f"Unable to get recording_dt from image {uploaded_file.name}, "
                                          f"consider supplying recording_dt manually")

    return datetime.strptime(recording_dt, '%Y:%m:%d %H:%M:%S')
