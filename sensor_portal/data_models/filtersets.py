import django_filters.rest_framework
from utils.filtersets import ExtraDataFilterMixIn, GenericFilterMixIn

from .models import DataFile, DataType, Deployment, Device, Project


class DataTypeFilter(GenericFilterMixIn):
    file_type = django_filters.BooleanFilter(
        method='is_file_type', label="file_type")
    device_type = django_filters.BooleanFilter(
        method='is_file_type', label="device_type")

    def is_file_type(self, queryset, name, value):
        print(name)
        if (name == "file_type"):
            return queryset.filter(files__isnull=not value)
        else:
            return queryset.filter(device_models__isnull=not value)


class DeploymentFilter(GenericFilterMixIn, ExtraDataFilterMixIn):

    class Meta:
        model = Deployment
        fields = GenericFilterMixIn.get_fields().copy()
        fields.update({
            'deployment_device_ID': ['exact', 'icontains', 'in'],
            'is_active': ['exact'],
            'deployment_start': ['exact', 'lte', 'gte'],
            'deployment_end': ['exact', 'lte', 'gte'],
            'site': ['exact', 'in'],
            'site__name': ['exact', 'icontains', 'in'],
            'site__short_name': ['exact', 'icontains', 'in'],
            'device': ['exact', 'in'],
            'device__device_ID': ['exact', 'icontains', 'in'],
            'device__name': ['exact', 'icontains', 'in'],
            'project': ['exact'],
            'project__project_ID': ['exact'],
            'device_type': ['exact', 'in'],
            'device_type__name': ['exact', 'icontains', 'in'],
        })


class ProjectFilter(GenericFilterMixIn):

    is_active = django_filters.BooleanFilter(
        field_name="deployments__is_active")

    class Meta:
        model = Project
        fields = GenericFilterMixIn.get_fields().copy()
        fields.update({
            'project_ID': ['exact', 'icontains', 'in'],
            'name': ['exact', 'icontains', 'in'],
            'organisation': ['exact', 'icontains', 'in'],
        })


class DeviceFilter(GenericFilterMixIn, ExtraDataFilterMixIn):
    is_active = django_filters.BooleanFilter(
        field_name="deployments__is_active")

    device_type = django_filters.ModelChoiceFilter(field_name='device__type',
                                                   queryset=DataType.objects.filter(
                                                       devices__isnull=False).distinct(),
                                                   label="device type")

    class Meta:
        model = Device
        fields = GenericFilterMixIn.get_fields().copy()
        fields.update({
            'type': ['exact', 'in'],
            'type__name': ['exact', 'icontains', 'in'],
            'device_ID': ['exact', 'icontains', 'in'],
            'model__name': ['exact', 'icontains', 'in'],
        })


class DataFileFilter(GenericFilterMixIn, ExtraDataFilterMixIn):
    is_favourite = django_filters.BooleanFilter(field_name='favourite_of',
                                                exclude=True,
                                                lookup_expr='isnull',
                                                label='is favourite')
    is_active = django_filters.BooleanFilter(
        field_name="deployment__is_active")

    device_type = django_filters.ModelChoiceFilter(field_name='deployment__device__type',
                                                   queryset=DataType.objects.filter(
                                                       devices__isnull=False).distinct(),
                                                   label="device type")

    class Meta:
        model = DataFile
        fields = GenericFilterMixIn.get_fields().copy()
        fields.update({
            'deployment': ['exact', 'in'],
            'deployment__deployment_device_ID': ['exact', 'in', 'icontains'],
            'deployment__device': ['exact', 'in'],
            'file_type': ['exact', 'in'],
            'file_type__name': ['exact', 'icontains', 'in'],
            'file_name': ['exact', 'icontains', 'in'],
            'file_size': ['lte', 'gte'],
            'file_format': ['exact', 'icontains', 'in'],
            'upload_dt': ['exact', 'gte', 'lte'],
            'recording_dt': ['exact', 'date__exact', 'gte', 'lte', 'date__gte', 'date__lte', 'time__gte', 'time__lte'],
            'local_storage': ['exact'],
            'archived': ['exact'],
            'original_name': ['exact', 'icontains', 'in'],
            'favourite_of': ['contains'],
        })
