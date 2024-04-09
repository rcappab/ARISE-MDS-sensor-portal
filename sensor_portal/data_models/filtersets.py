import django_filters.rest_framework
from .models import *


class GenericFilter(django_filters.FilterSet):
    created_after = django_filters.DateFilter(field_name='created_on', lookup_expr='gt')
    created_before = django_filters.DateFilter(field_name='created_on', lookup_expr='lte')

    class Meta:
        fields = {
            'id': ['exact', 'in']
        }


class ExtraInfoFilterMixIn(django_filters.FilterSet):
    extra_info = django_filters.CharFilter(method='extra_info_filter')

    def extra_info_filter(self, queryset, name, value):
        # unpack value
        newvalue = value.split("__")[-1]
        newname = "__".join(value.split("__")[:-1])
        newname = name + "__" + newname
        return queryset.filter(**{
            newname: newvalue,
        })


class DeploymentFilter(GenericFilter, ExtraInfoFilterMixIn):
    class Meta:
        model = Deployment
        fields = GenericFilter.Meta.fields.copy()
        fields.update({
            'deployment_deviceID': ['exact', 'icontains', 'in'],
            'is_active': ['exact'],
            'deploymentStart': ['exact', 'lte', 'gte'],
            'deploymentEnd': ['exact', 'lte', 'gte'],
            'site': ['exact', 'in'],
            'site__name': ['exact', 'icontains', 'in'],
            'site__short_name': ['exact', 'icontains', 'in'],
            'device': ['exact', 'in'],
            'device__deviceID': ['exact', 'icontains', 'in'],
            'device__name': ['exact', 'icontains', 'in'],
            'project': ['exact'],
            'project__projectID': ['exact'],
            'device_type': ['exact', 'in'],
            'device_type__name': ['exact', 'icontains', 'in'],
        })


class ProjectFilter(GenericFilter):
    class Meta:
        model = Project
        fields = GenericFilter.Meta.fields.copy()
        fields.update({
            'projectID': ['exact', 'icontains', 'in'],
            'projectName': ['exact', 'icontains', 'in'],
            'organizationName': ['exact', 'icontains', 'in'],
        })


class DeviceFilter(GenericFilter, ExtraInfoFilterMixIn):
    class Meta:
        model = Device
        fields = GenericFilter.Meta.fields.copy()
        fields.update({
            'type': ['exact', 'in'],
            'type__name': ['exact', 'icontains', 'in'],
            'deviceID': ['exact', 'icontains', 'in'],
            'make': ['exact', 'icontains', 'in'],
            'model': ['exact', 'icontains', 'in'],
        })


class DataFileFilter(GenericFilter, ExtraInfoFilterMixIn):
    is_favourite = django_filters.BooleanFilter(field_name='favourite_of',
                                                exclude=True,
                                                lookup_expr='isnull',
                                                label='is favourite')
    class Meta:
        model = DataFile
        fields = GenericFilter.Meta.fields.copy()
        fields.update({
            'deployment': ['exact', 'in'],
            'deployment__deployment_deviceID': ['exact', 'in', 'icontains'],
            'deployment__device': ['exact', 'in'],
            'file_type': ['exact', 'in'],
            'file_type__name': ['exact', 'icontains', 'in'],
            'file_name': ['exact', 'icontains', 'in'],
            'file_size': ['lte', 'gte'],
            'file_format': ['exact', 'icontains', 'in'],
            'upload_date': ['exact', 'gte', 'lte'],
            'recording_dt': ['exact', 'date__exact', 'gte', 'lte', 'date__gte', 'date__lte', 'time__gte', 'time__lte'],
            'localstorage': ['exact'],
            'archived': ['exact'],
            'original_name': ['exact', 'icontains', 'in'],
            'favourite_of': ['contains']
        })
