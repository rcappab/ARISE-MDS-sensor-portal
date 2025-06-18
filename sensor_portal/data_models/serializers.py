from datetime import datetime as dt

from bridgekeeper import perms
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import timezone as djtimezone
from PIL import ExifTags, Image
from rest_framework import serializers
from rest_framework_gis import serializers as geoserializers
from timezone_field.rest_framework import TimeZoneSerializerField
from utils.serializers import (CheckFormMixIn, CreatedModifiedMixIn,
                               InstanceGetMixIn, ManagerMixIn, OwnerMixIn,
                               SlugRelatedGetOrCreateField)
from utils.validators import check_two_keys

from . import validators
from .models import (DataFile, DataType, Deployment, Device, DeviceModel,
                     Project, Site)


class DeploymentFieldsMixIn(InstanceGetMixIn, OwnerMixIn, CreatedModifiedMixIn, CheckFormMixIn,
                            serializers.ModelSerializer):
    """
    A mixin serializer for handling deployment-related fields and operations.
    This serializer provides functionality for managing deployment data, including
    relationships with devices, projects, sites, and time zones. It also includes
    validation logic for ensuring data integrity and permissions.
    Attributes:
        device_type (SlugRelatedField): A slug-related field for the device type, linked to `DataType`.
        device_type_ID (PrimaryKeyRelatedField): A primary key-related field for the device type, linked to `DataType`.
        device (SlugRelatedField): A slug-related field for the device, linked to `Device`.
        device_ID (PrimaryKeyRelatedField): A primary key-related field for the device, linked to `Device`.
        project (SlugRelatedField): A slug-related field for projects, excluding the global project.
        project_ID (PrimaryKeyRelatedField): A primary key-related field for projects, excluding the global project.
        site (SlugRelatedGetOrCreateField): A slug-related field for the site, linked to `Site`.
        site_ID (PrimaryKeyRelatedField): A primary key-related field for the site, linked to `Site`.
        time_zone (TimeZoneSerializerField): A field for handling time zones, using pytz.
        deployment_start (DateTimeField): A datetime field for the deployment start time, defaulting to UTC.
        deployment_end (DateTimeField): A datetime field for the deployment end time, defaulting to UTC.
    Methods:
        to_representation(instance):
            Customizes the representation of the serialized data, including filtering projects
            and checking permissions.
        create(*args, **kwargs):
            Creates a new deployment instance and saves it.
        update(*args, **kwargs):
            Updates an existing deployment instance and saves it.
        validate(data):
            Validates the input data, ensuring relationships and constraints are met, such as
            device and site attachments, deployment type compatibility, and time overlap checks.
    Meta:
        model (Deployment): Specifies the model associated with this serializer.
        exclude (list): Excludes the `last_image` field from serialization.
    Notes:
        - This mixin includes validation logic for deployment-related constraints.
        - Permissions are checked for managing deployments.
        - Handles both slug and primary key relationships for related fields.
    """

    device_type = serializers.SlugRelatedField(
        slug_field='name', queryset=DataType.objects.all(), required=False, allow_null=True)
    device_type_ID = serializers.PrimaryKeyRelatedField(source="device_type", queryset=DataType.objects.all(),
                                                        required=False, allow_null=True)
    device = serializers.SlugRelatedField(
        slug_field='device_ID', queryset=Device.objects.all(), required=False)
    device_ID = serializers.PrimaryKeyRelatedField(source="device", queryset=Device.objects.all(),
                                                   required=False)
    project = serializers.SlugRelatedField(many=True,
                                           slug_field='project_ID',
                                           queryset=Project.objects.all().exclude(name=settings.GLOBAL_PROJECT_ID),
                                           allow_null=True,
                                           required=False)
    project_ID = serializers.PrimaryKeyRelatedField(source="project",
                                                    many=True,
                                                    queryset=Project.objects.all().exclude(name=settings.GLOBAL_PROJECT_ID),
                                                    required=False,
                                                    allow_null=True)
    site = SlugRelatedGetOrCreateField(slug_field='short_name',
                                       queryset=Site.objects.all(),
                                       required=False, allow_null=True)
    site_ID = serializers.PrimaryKeyRelatedField(source="site", queryset=Site.objects.all(),
                                                 required=False, allow_null=True)

    time_zone = TimeZoneSerializerField(use_pytz=True)

    # always return in UTC regardless of server setting
    deployment_start = serializers.DateTimeField(
        default=djtimezone.now(), default_timezone=djtimezone.utc)
    deployment_end = serializers.DateTimeField(
        default_timezone=djtimezone.utc, required=False, allow_null=True)

    # check project permissions here or in viewpoint

    def to_representation(self, instance):
        """
        Customizes the representation of a model instance for serialization.
        Args:
            instance (object): The model instance to be serialized.
        Returns:
            dict: A dictionary representation of the instance, with modifications
            based on the context and user permissions.
        Details:
            - Extracts the `request` user from the serializer context.
            - Modifies the representation to exclude global projects.
            - Adds a `can_manage` field based on user permissions.
            - Removes the `thumb_url` field if the request context is not available.
            - If the representation contains `properties`, it adjusts the structure
              to include the modified properties within a GeoJSON-like format.
        """

        request_user = self.context['request'].user
        initial_rep = super(DeploymentFieldsMixIn,
                            self).to_representation(instance)
        if initial_rep.get('properties') is not None:
            geojson_rep = initial_rep
            initial_rep = initial_rep.get('properties')
        else:
            geojson_rep = None

        projects_no_global = [(x, y) for x, y in zip(
            initial_rep["project"], initial_rep["project_ID"]) if x != settings.GLOBAL_PROJECT_ID]

        initial_rep["project"], initial_rep["project_ID"] = zip(
            *projects_no_global) if projects_no_global else ([], [])
        initial_rep["can_manage"] = perms['data_models.change_deployment'].check(
            request_user, instance)

        if not self.context.get('request'):
            initial_rep.pop('thumb_url')

        if geojson_rep is not None:
            geojson_rep['properties'] = initial_rep

        return initial_rep

    class Meta:
        model = Deployment
        exclude = ['last_image']

    def __init__(self, *args, **kwargs):
        """
        Initializes the DeploymentFieldsMixIn class.
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        Attributes:
            clear_project (bool): A flag indicating whether to clear the project. Defaults to False.
            management_perm (str): The permission string for managing deployments.
        """

        self.clear_project = False
        self.management_perm = 'data_models.change_deployment'
        super(DeploymentFieldsMixIn, self).__init__(*args, **kwargs)

    def create(self, *args, **kwargs):
        """
        Overrides the create method to handle the creation of an instance.
        This method calls the parent class's create method to initialize the instance,
        saves the instance to the database, and then returns the created instance.
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        Returns:
            instance: The created and saved instance.
        """

        instance = super(DeploymentFieldsMixIn, self).create(*args, **kwargs)
        instance.save()
        return instance

    def update(self, *args, **kwargs):
        """
        Update the instance with the provided arguments and save the changes.
        This method overrides the `update` method from the parent class to ensure
        that the instance is saved after being updated.
        Args:
            *args: Variable length argument list passed to the parent class's `update` method.
            **kwargs: Arbitrary keyword arguments passed to the parent class's `update` method.
        Returns:
            instance: The updated and saved instance.
        """

        instance = super(DeploymentFieldsMixIn, self).update(*args, **kwargs)
        instance.save()
        return instance

    def validate(self, data):
        """
        Validates the input data for the serializer.
        This method performs several checks to ensure the integrity and validity of the data being processed:
        - Ensures that a `project` is set if `form_submission` is active and `project` is not provided.
        - Validates the data using the parent class's `validate` method.
        - Checks if a `device` or `device_ID` is attached when the request is not partial.
        - Checks if a `site` or `site_ID` is attached when the request is not partial.
        - Validates the compatibility between `device_type` and `device`.
        - Ensures that the deployment start time is not after the deployment end time.
        - Checks for overlapping deployments for the given `device`.
        Args:
            data (dict): The input data to validate.
        Returns:
            dict: The validated data.
        Raises:
            serializers.ValidationError: If any of the validation checks fail.
        """

        if self.form_submission & (data.get('project') is None):
            data['project'] = []

        data = super().validate(data)

        # #check if a device type has been set via either method
        # result, message, data = validators.check_two_keys(
        #     'device_type',
        #     'device_type_ID',
        #     data,
        #     DataType
        # )
        # if not result:
        #     raise serializers.ValidationError(message)

        if not self.partial:
            # check if a device has been attached (via either method)
            result, message, data = check_two_keys(
                'device',
                'device_ID',
                data,
                Device,
                self.form_submission
            )
            if not result:
                raise serializers.ValidationError(message)

            # check if a site has been attached (via either method)
            result, message, data = check_two_keys(
                'site',
                'site_ID',
                data,
                Site,
                self.form_submission
            )
            if not result:
                raise serializers.ValidationError(message)

        result, message = validators.deployment_check_type(self.instance_get('device_type', data),
                                                           self.instance_get('device', data))
        if not result:
            raise serializers.ValidationError(message)

        result, message = validators.deployment_start_time_after_end_time(self.instance_get('deployment_start', data),
                                                                          self.instance_get('deployment_end', data))
        if not result:
            raise serializers.ValidationError(message)

        result, message = validators.deployment_check_overlap(self.instance_get('deployment_start', data),
                                                              self.instance_get(
                                                                  'deployment_end', data),
                                                              self.instance_get(
                                                                  'device', data),
                                                              self.instance_get('id', data))
        if not result:
            raise serializers.ValidationError(message)

        return data


class DeploymentSerializer(DeploymentFieldsMixIn, serializers.ModelSerializer):
    """
    Serializer for the Deployment model.
    This serializer inherits from DeploymentFieldsMixIn and serializers.ModelSerializer.
    It is used to serialize and deserialize Deployment model instances, excluding specific fields.
    Attributes:
        Meta:
            model (Deployment): The model class to be serialized.
            exclude (list): A list of fields to be excluded from serialization, 
                            combining DeploymentFieldsMixIn.Meta.exclude and the 'point' field.
    """

    class Meta:
        model = Deployment
        exclude = DeploymentFieldsMixIn.Meta.exclude+['point']


class DeploymentSerializer_GeoJSON(DeploymentFieldsMixIn, geoserializers.GeoFeatureModelSerializer):
    """
    Serializer for deployment data in GeoJSON format.
    This serializer extends `GeoFeatureModelSerializer` to include deployment-specific fields
    and functionality. It uses the `point` field as the geographic representation.
    Attributes:
        Meta.geo_field (str): Specifies the geographic field used for GeoJSON serialization.
    """

    def __init__(self, *args, **kwargs):
        self.Meta.geo_field = "point"
        super(DeploymentSerializer_GeoJSON, self).__init__(*args, **kwargs)


class ProjectSerializer(OwnerMixIn, ManagerMixIn, CreatedModifiedMixIn, serializers.ModelSerializer):
    """
    Serializer for the Project model, incorporating mixins for ownership, management, 
    and tracking creation/modification timestamps.
    Attributes:
        is_active (serializers.BooleanField): A read-only field indicating whether the project is active.
    Meta:
        model (Project): The model associated with this serializer.
        exclude (list): Specifies fields to exclude from serialization. Currently, no fields are excluded.
    Methods:
        __init__(*args, **kwargs): Initializes the serializer and sets the management permission 
        required for modifying the project.
    """

    is_active = serializers.BooleanField(
        read_only=True)

    class Meta:
        model = Project
        exclude = []

    def __init__(self, *args, **kwargs):
        self.management_perm = 'data_models.change_project'
        super(ProjectSerializer, self).__init__(*args, **kwargs)


class DeviceModelSerializer(CreatedModifiedMixIn, OwnerMixIn, serializers.ModelSerializer):
    """
    Serializer for the DeviceModel model, providing serialization and deserialization
    functionality for DeviceModel instances. This serializer includes additional mixins
    for handling created/modified timestamps and ownership.
    Attributes:
        type (SlugRelatedField): A field that maps the 'type' attribute of the model to 
            the 'name' field of the related DataType model. It is optional.
        type_ID (PrimaryKeyRelatedField): A field that maps the 'type' attribute of the model 
            to the primary key of the related DataType model. It is optional.
    Meta:
        model (DeviceModel): Specifies the model associated with this serializer.
        exclude (list): Specifies fields to exclude from serialization. Currently, no fields are excluded.
    Methods:
        to_representation(instance):
            Overrides the default representation method to include additional fields
            related to the data handler. If a handler is found for the given type and name,
            its full name and ID are added to the serialized representation. Otherwise,
            these fields are set to None.
    """

    type = serializers.SlugRelatedField(
        slug_field='name', queryset=DataType.objects.all(), required=False)
    type_ID = serializers.PrimaryKeyRelatedField(source="type", queryset=DataType.objects.all(),
                                                 required=False)

    class Meta:
        model = DeviceModel
        exclude = []

    def to_representation(self, instance):
        """
        Override the `to_representation` method to customize the serialized representation 
        of the `DeviceModelSerializer` instance.
        This method adds additional fields `data_handler` and `data_handler_id` to the 
        serialized output based on the presence of a data handler for the given device type 
        and name.
        Args:
            instance: The instance of the model being serialized.
        Returns:
            dict: A dictionary containing the serialized representation of the instance, 
            including the additional `data_handler` and `data_handler_id` fields.
        """

        initial_rep = super(DeviceModelSerializer,
                            self).to_representation(instance)

        handler = settings.DATA_HANDLERS.get_handler(
            instance.type.name, instance.name)
        if handler:
            initial_rep["data_handler"] = handler.full_name
            initial_rep["data_handler_id"] = handler.id
        else:
            initial_rep["data_handler"] = None
            initial_rep["data_handler_id"] = None
        return initial_rep


class DeviceSerializer(OwnerMixIn, ManagerMixIn, CreatedModifiedMixIn, CheckFormMixIn, serializers.ModelSerializer):
    """
    Serializer for the Device model, providing functionality for serialization and deserialization
    of Device instances. This serializer includes custom validation, representation logic, and 
    additional fields for handling related models and user permissions.
    Attributes:
        type (SlugRelatedField): A slug-related field for the 'type' attribute, linked to the DataType model.
        type_ID (PrimaryKeyRelatedField): A primary key related field for the 'type' attribute, linked to the DataType model.
        model (SlugRelatedField): A slug-related field for the 'model' attribute, linked to the DeviceModel model.
        model_ID (PrimaryKeyRelatedField): A primary key related field for the 'model' attribute, linked to the DeviceModel model.
        username (CharField): A field for the username, optional.
        password (CharField): A write-only field for the password, optional.
        is_active (BooleanField): A read-only field indicating whether the device is active.
    Meta:
        model (Device): Specifies the Device model as the target for serialization.
        exclude (list): Excludes no fields from serialization.
    Methods:
        __init__(*args, **kwargs):
            Initializes the serializer and sets the management permission required for certain operations.
        to_representation(instance):
            Customizes the representation of the serialized data, including conditional field removal 
            based on user permissions and adding data handler information.
        validate(data):
            Validates the input data, ensuring required fields are provided and checks relationships 
            between 'model' and 'model_ID'.
    """

    type = serializers.SlugRelatedField(
        slug_field='name', queryset=DataType.objects.all(), required=False)
    type_ID = serializers.PrimaryKeyRelatedField(source="type", queryset=DataType.objects.all(),
                                                 required=False)
    model = serializers.SlugRelatedField(
        slug_field='name', queryset=DeviceModel.objects.all(), required=False)
    model_ID = serializers.PrimaryKeyRelatedField(source="model", queryset=DeviceModel.objects.all(),
                                                  required=False)

    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False, write_only=True)
    is_active = serializers.BooleanField(
        read_only=True)

    class Meta:
        model = Device
        exclude = []

    def __init__(self, *args, **kwargs):
        self.management_perm = 'data_models.change_device'
        super(DeviceSerializer, self).__init__(*args, **kwargs)

    def to_representation(self, instance):
        """
        Customize the representation of the serialized data for a Device instance.
        This method modifies the default representation by removing sensitive fields
        such as 'password' and conditionally removing other fields like 'username'
        based on the user's permissions. Additionally, it adds information about the
        data handler associated with the device type and model.
        Args:
            instance (Device): The instance of the Device model being serialized.
        Returns:
            dict: A dictionary representing the serialized data with modifications.
              Includes the following keys:
              - 'data_handler': Full name of the associated data handler or None.
              - 'data_handler_id': ID of the associated data handler or None.
              Sensitive fields are removed based on user permissions.
        """

        initial_rep = super(DeviceSerializer, self).to_representation(instance)
        fields_to_pop = [
            "username"
        ]
        fields_to_always_pop = [
            "password"
        ]
        [initial_rep.pop(field, '') for field in fields_to_always_pop]
        if self.context.get('request'):
            user_is_manager = self.context['request'].user.has_perm(
                self.management_perm, obj=instance)
        else:
            user_is_manager = False
        if not user_is_manager:
            [initial_rep.pop(field, '') for field in fields_to_pop]

        handler = settings.DATA_HANDLERS.get_handler(
            instance.type.name, instance.model.name)
        if handler:
            initial_rep["data_handler"] = handler.full_name
            initial_rep["data_handler_id"] = handler.id
        else:
            initial_rep["data_handler"] = None
            initial_rep["data_handler_id"] = None

        return initial_rep

    def validate(self, data):
        """
        Validates the input data for the serializer.
        This method first calls the parent class's `validate` method to perform
        base validation. Then, it performs additional checks to ensure that a 
        model has been attached either via the 'model' key or the 'model_ID' key 
        in the data. If the serializer is not in partial mode and the required 
        keys are not present, a validation error is raised.
        Args:
            data (dict): The input data to be validated.
        Returns:
            dict: The validated data.
        Raises:
            serializers.ValidationError: If the required keys ('model' or 'model_ID') 
            are not present in the data when the serializer is not in partial mode.
        """

        data = super().validate(data)

        if not self.partial:
            # check if a model has been attached (via either method)
            result, message, data = check_two_keys(
                'model',
                'model_ID',
                data,
                Device,
                self.form_submission
            )
            if not result:
                raise serializers.ValidationError(message)

        return data


class DataFileCheckSerializer(serializers.Serializer):
    """
        Serializer for use when checking if a file is already present in the system.
        Attributes:
            file_names(ListField(CharField)): List of filenames to check in the system.
            original_names(ListField(CharField)): List of original file names to check in the system.
    """
    file_names = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    original_names = serializers.ListField(
        child=serializers.CharField(), required=False
    )


class DataFileSerializer(CreatedModifiedMixIn, serializers.ModelSerializer):
    """
    Serializer for the DataFile model, providing serialization and deserialization
    functionality for DataFile instances. This serializer includes custom validation
    and representation logic.
    Attributes:
        deployment (SlugRelatedField): A field representing the deployment associated
            with the data file, using the deployment_device_ID as the slug field.
        deployment_ID (PrimaryKeyRelatedField): A field representing the deployment
            associated with the data file, using the primary key.
        file_type (StringRelatedField): A field representing the type of the file as a
            string.
        recording_dt (DateTimeField): A field representing the recording date and time
            of the data file, with a default timezone set to UTC.
    Methods:
        to_representation(instance):
            Customizes the serialized representation of the DataFile instance. Adds
            additional fields such as 'favourite' and 'can_annotate' based on the
            request context. Excludes certain fields depending on the presence of a
            request context.
        validate(data):
            Validates the serialized data to ensure the recording date and deployment
            are consistent with the defined rules. Raises a ValidationError if the
            validation fails.
    Meta:
        model (DataFile): Specifies the model associated with this serializer.
        exclude (list): A list of fields to exclude from the serialized representation.
    """

    deployment = serializers.SlugRelatedField(
        slug_field='deployment_device_ID', queryset=Deployment.objects.all(), required=False)
    deployment_ID = serializers.PrimaryKeyRelatedField(source="deployment", queryset=Deployment.objects.all(),
                                                       required=False)
    file_type = serializers.StringRelatedField()
    recording_dt = serializers.DateTimeField(default_timezone=djtimezone.utc)

    def to_representation(self, instance):
        initial_rep = super(DataFileSerializer,
                            self).to_representation(instance)
        if self.context.get('request'):
            request_user = self.context['request'].user
            initial_rep["favourite"] = instance.favourite_of.all().filter(
                pk=request_user.pk).exists()
            initial_rep.pop('path')
            initial_rep["can_annotate"] = perms['data_models.annotate_datafile'].check(
                request_user, instance)
        else:
            to_exclude = ["file_url", "thumb_url"]
            [initial_rep.pop(x) for x in to_exclude]
        return initial_rep

    class Meta:
        model = DataFile
        exclude = ["do_not_remove", "local_path", "favourite_of",
                   "tar_file", "archived", "local_storage"]

    def validate(self, data):
        data = super().validate(data)

        result, message = validators.data_file_in_deployment(
            data.get('recording_dt', self.instance.recording_dt), data.get('deployment', self.instance.deployment))
        if not result:
            raise serializers.ValidationError(message)
        return data


class DataFileUploadSerializer(serializers.Serializer):
    """
    Serializer for handling data file uploads with associated metadata.
    Attributes:
        device (CharField): Optional device name associated with the upload.
        device_ID (IntegerField): Optional device ID associated with the upload.
        deployment (CharField): Optional deployment name associated with the upload.
        deployment_ID (IntegerField): Optional deployment ID associated with the upload.
        files (ListField): Required list of files to be uploaded. Each file must not be empty.
        file_names (ListField): Optional list of file names corresponding to the uploaded files.
        extra_data (ListField): Optional list of JSON objects containing additional metadata.
        recording_dt (ListField): Optional list of recording date-times for the uploaded files.
        autoupdate (BooleanField): Flag indicating whether to auto-update the deployment. Defaults to False.
        rename (BooleanField): Flag indicating whether to rename the uploaded files. Defaults to True.
        check_filename (BooleanField): Flag indicating whether to validate filenames. Defaults to True.
        data_types (ListField): Optional list of data types associated with the upload, linked to DataType objects.
        is_active (BooleanField): Read-only field indicating whether the associated deployment is active.
    Methods:
        create(validated_data):
            Returns the validated data without modification.
        validate(data):
            Validates the input data, ensuring that either a deployment or device is provided.
            Checks if the specified deployment or device exists.
            Validates the recording date-times if provided, ensuring they match the number of uploaded files.
        update(validated_data):
            Placeholder method for updating data. Not implemented.
    """

    device = serializers.CharField(required=False)
    device_ID = serializers.IntegerField(required=False)
    deployment = serializers.CharField(required=False)
    deployment_ID = serializers.IntegerField(required=False)

    files = serializers.ListField(child=serializers.FileField(
        allow_empty_file=False, max_length=None), required=True)
    file_names = serializers.ListField(child=serializers.CharField(
    ), required=False)
    extra_data = serializers.ListField(
        child=serializers.JSONField(binary=True), required=False)
    recording_dt = serializers.ListField(
        child=serializers.DateTimeField(), required=False)
    autoupdate = serializers.BooleanField(default=False)
    rename = serializers.BooleanField(default=True)
    check_filename = serializers.BooleanField(default=True)
    data_types = serializers.ListField(child=serializers.SlugRelatedField(slug_field='name',
                                                                          queryset=DataType.objects.all()),
                                       required=False)
    is_active = serializers.BooleanField(
        source="deployment.is_active", read_only=True)

    def create(self, validated_data):
        return validated_data

    def validate(self, data):
        data = super().validate(data)
        deployment = data.get('deployment')
        deployment_ID = data.get('deployment_ID')
        device = data.get('device')
        device_ID = data.get('device_ID')

        #  Check a deployment or device is supplied
        if deployment is None and deployment_ID is None and device is None and device_ID is None:
            raise serializers.ValidationError(
                "A deployment or a device must be supplied")

        # Check if deployment or device exists
        if deployment or deployment_ID:
            try:
                deployment_object = Deployment.objects.get(Q(Q(deployment_device_ID=deployment) |
                                                             Q(pk=deployment_ID)))
            except ObjectDoesNotExist:
                raise serializers.ValidationError({"deployment":
                                                   f"Deployment {deployment} does not exist",
                                                   "deployment_ID": f"Deployment ID {deployment_ID} does not exist"})
            data['deployment_object'] = deployment_object
            data['device_object'] = deployment_object.device
        elif device or device_ID:
            try:
                device_object = Device.objects.get(
                    Q(Q(device_ID=device) | Q(pk=device_ID)))
            except ObjectDoesNotExist:
                raise serializers.ValidationError({"device":
                                                   f"Device {device} does not exist",
                                                   "device_ID": f"Device ID {device_ID} does not exist"})
            data['device_object'] = device_object

        files = data.get("files")
        recording_dt = data.get('recording_dt')
        if files:
            #  if not an image, user must supply the recording date time
            # is_not_image = ["image" not in magic.from_buffer(
            #     x.read(), mime=True) for x in files]
            # if any(is_not_image) and recording_dt is None:
            #     raise serializers.ValidationError(
            #         {"recording_dt": "Recording date times can only be extracted from images, please provide 'recording_dt' or upload only images"})

            #  check recording_dt and number of files match
            if recording_dt is not None:

                if len(recording_dt) > 1 and len(recording_dt) != len(data.get('files')):
                    raise serializers.ValidationError(
                        {"recording_dt": "More than one recording_dt was supplied, but the number does not match the number of files"})

        return data

    def update(self, validated_data):
        # Not used
        pass


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = '__all__'


class DataTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataType
        fields = '__all__'


class GenericJobSerializer(serializers.Serializer):
    """
    Serializer for displaying generic jobs.

    Attributes:
        id(IntegerField): Numeric ID of the generic job.
        name(CharField): Name of the generic job.
        task_name(CharField): Celery task name of the generic job.
        data_type(CharField): Type of data the job expects, e.g. "datafile"
        admin_only(BooleanField): True if only a superuser view/start this job.
        max_items(IntegerField): Maximum number of items that can be processed by the job.
        default_args(JSONField): Default arguments for the job, stored as a JSON object.
    """
    id = serializers.IntegerField()
    name = serializers.CharField()
    task_name = serializers.CharField()
    data_type = serializers.CharField()
    admin_only = serializers.BooleanField()
    max_items = serializers.IntegerField()
    default_args = serializers.JSONField()
