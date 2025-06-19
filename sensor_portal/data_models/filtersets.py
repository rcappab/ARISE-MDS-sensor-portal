import django_filters.rest_framework
from django.db.models import BooleanField, Case, ExpressionWrapper, F, Q, When
from observation_editor.models import Observation
from utils.filtersets import ExtraDataFilterMixIn, GenericFilterMixIn

from .models import (DataFile, DataType, Deployment, Device, DeviceModel,
                     Project)


class DataTypeFilter(GenericFilterMixIn):
    """
    A filter class for filtering data types based on file type or device type.
    Attributes:
        file_type (django_filters.BooleanFilter): A filter for determining if the data is of file type.
        device_type (django_filters.BooleanFilter): A filter for determining if the data is of device type.
    Methods:
        is_file_type(queryset, name, value):
            Filters the queryset based on the provided filter name and value.
            If the filter name is "file_type", the original queryset is returned.
            Otherwise, filters the queryset to include or exclude device models based on the value.
    """

    file_type = django_filters.BooleanFilter(
        method='is_file_type', label="file_type")
    device_type = django_filters.BooleanFilter(
        method='is_file_type', label="device_type")

    def is_file_type(self, queryset, name, value):
        """
        Filters a queryset based on the provided `name` and `value`.
        If the `name` parameter is "file_type", the original queryset is returned without filtering.
        Otherwise, the queryset is filtered based on whether `device_models` is null or not,
        determined by the negation of the `value` parameter.
        Args:
            queryset (QuerySet): The initial queryset to be filtered.
            name (str): The name of the filter parameter.
            value (bool): The value used to determine the filtering condition.
        Returns:
            QuerySet: The filtered queryset.
        """

        if (name == "file_type"):
            return queryset
        else:
            return queryset.filter(device_models__isnull=not value)


class DeploymentFilter(GenericFilterMixIn, ExtraDataFilterMixIn):
    """
    A filter class for filtering Deployment objects based on various criteria.
    This class extends `GenericFilterMixIn` and `ExtraDataFilterMixIn` to provide
    additional filtering capabilities for Deployment objects.
    Attributes:
        Meta.model (Deployment): Specifies the model to be filtered.
        Meta.fields (dict): A dictionary defining the fields and their respective
            filtering options. The fields include:
            - `deployment_device_ID`: Filters by exact match, case-insensitive containment, or inclusion in a list.
            - `is_active`: Filters by exact match.
            - `deployment_start`: Filters by exact match, less than or equal to, or greater than or equal to.
            - `deployment_end`: Filters by exact match, less than or equal to, or greater than or equal to.
            - `site`: Filters by exact match or inclusion in a list.
            - `site__name`: Filters by exact match, case-insensitive containment, or inclusion in a list.
            - `site__short_name`: Filters by exact match, case-insensitive containment, or inclusion in a list.
            - `device__id`: Filters by exact match or inclusion in a list.
            - `device__device_ID`: Filters by exact match, case-insensitive containment, or inclusion in a list.
            - `device__name`: Filters by exact match, case-insensitive containment, or inclusion in a list.
            - `project__id`: Filters by exact match.
            - `project__project_ID`: Filters by exact match.
            - `device_type`: Filters by exact match or inclusion in a list.
            - `device_type__name`: Filters by exact match, case-insensitive containment, or inclusion in a list.
    This filter class is designed to be used in scenarios where complex filtering
    of Deployment objects is required, such as in APIs or data querying interfaces.
    """

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
            'device__id': ['exact', 'in'],
            'device__device_ID': ['exact', 'icontains', 'in'],
            'device__name': ['exact', 'icontains', 'in'],
            'project__id': ['exact'],
            'project__project_ID': ['exact'],
            'device_type': ['exact', 'in'],
            'device_type__name': ['exact', 'icontains', 'in'],
        })


class ProjectFilter(GenericFilterMixIn):
    """
    ProjectFilter is a filter class used to filter Project model instances based on various criteria.
    Attributes:
        is_active (django_filters.BooleanFilter): A filter for checking if the related deployments are active.
    Meta:
        model (Project): The model associated with this filter.
        fields (dict): A dictionary of fields and their filtering options. Includes:
            - 'project_ID': Filters by exact match, case-insensitive containment, or inclusion in a list.
            - 'name': Filters by exact match, case-insensitive containment, or inclusion in a list.
            - 'organisation': Filters by exact match, case-insensitive containment, or inclusion in a list.
    """

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
    """
    DeviceFilter is a filter class used to filter Device objects based on various criteria.
    Attributes:
        is_active (django_filters.BooleanFilter): Filters devices based on the active status of their deployments.
        device_type (django_filters.ModelChoiceFilter): Filters devices by their type. The queryset is restricted to 
            DataType objects associated with devices.
    Meta:
        model (Device): Specifies the model to be filtered.
        fields (dict): Defines the fields and lookup expressions available for filtering. Includes:
            - 'type': Filters by exact match or inclusion in a list.
            - 'type__name': Filters by exact match, case-insensitive containment, or inclusion in a list.
            - 'device_ID': Filters by exact match, case-insensitive containment, or inclusion in a list.
            - 'model__name': Filters by exact match, case-insensitive containment, or inclusion in a list.
    """

    is_active = django_filters.BooleanFilter(
        field_name="deployments__is_active")

    device_type = django_filters.ModelChoiceFilter(field_name='type',
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
    """
    DataFileFilter is a Django FilterSet class designed to filter DataFile objects based on various criteria. 
    It provides a set of filters for querying DataFile instances, including filters for deployment details, 
    file attributes, observation types, and user-specific conditions.
    Filters:
    ---------
    - is_favourite: Filters files that are marked as favorites.
    - is_active: Filters files based on the active status of their deployment.
    - device_type: Filters files by the type of device associated with their deployment.
    - has_observations: Filters files that have associated observations.
    - obs_type: Filters files based on the type of observations (e.g., human, AI, or none).
    - uncertain: Filters files based on the uncertainty of observations (e.g., validation requested).
    Methods:
    --------
    - filter_obs_type(queryset, name, value): Custom method to filter files based on observation types.
    - filter_uncertain(queryset, name, value): Custom method to filter files based on uncertainty in observations.
    Meta:
    -----
    - model: Specifies the DataFile model to be filtered.
    - fields: Defines the fields and their lookup expressions for filtering.
    Usage:
    ------
    This filterset can be used in Django views or APIs to provide advanced filtering capabilities for DataFile objects.
    """

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

    has_observations = django_filters.BooleanFilter(
        field_name="observations", lookup_expr="isnull", exclude=True, label="Has observations")

    obs_type = django_filters.ChoiceFilter(
        choices=[
            ("no_obs", "No observations"),
            ("no_human_obs", "No human observations"),
            ("all_obs", "All observations"),
            ("has_human", "Human observations"),
            ("has_ai", "AI observations"),
            ("human_only", "Human observations only"),
            ("ai_only", "AI observations only"),
        ],
        method="filter_obs_type",
        label="Observation type"
    )

    def filter_obs_type(self, queryset, name, value):
        """
        Filters a queryset based on the type of observations associated with it.
        Args:
            queryset (QuerySet): The initial queryset to filter.
            name (str): The name of the filter field (unused in this method).
            value (str): The filter value indicating the type of observations to filter by. 
                 Accepted values are:
                 - "no_obs": Filters items with no observations.
                 - "no_human_obs": Excludes items with observations from a human source.
                 - "all_obs": Filters items with at least one observation.
                 - "has_human": Filters items with observations from a human source.
                 - "has_ai": Filters items with observations from non-human sources (AI).
                 - "ai_only": Filters items with observations from non-human sources (AI) only.
                 - "human_only": Filters items with observations from human sources only.
        Returns:
            QuerySet: The filtered queryset based on the specified observation type.
        """

        if value == "no_obs":
            return queryset.filter(observations__isnull=True)
        elif value == "no_human_obs":
            return queryset.exclude(observations__source="human")
        elif value == "all_obs":
            return queryset.filter(observations__isnull=False)
        elif value == "has_human":
            return queryset.filter(observations__source="human")
        elif value == "has_ai":
            return queryset.filter(observations__in=Observation.objects.all().exclude(source="human"))
        elif value == "ai_only":
            return queryset.filter(observations__isnull=False).exclude(observations__source="human")
        elif value == "human_only":
            return queryset.filter(observations__source="human").exclude(observations__in=Observation.objects.all().exclude(source="human"))

    uncertain = django_filters.ChoiceFilter(
        choices=[
            ("no_uncertain", "No uncertain observations"),
            ("uncertain", "Uncertain observations"),
            ("other_uncertain", "Other's uncertain observations"),
            ("my_uncertain", "My uncertain observations"),
        ],
        method="filter_uncertain",
        label="Uncertain observations"
    )

    def filter_uncertain(self, queryset, name, value):
        """
        Filters a queryset based on the uncertainty status of observations.
        Args:
            queryset (QuerySet): The initial queryset to filter.
            name (str): The name of the filter field (unused in this method).
            value (str): The filter value indicating the type of uncertainty to apply. 
                         Accepted values are:
                         - "no_uncertain": Filters observations that are either null or not marked for validation.
                         - "uncertain": Filters observations marked for validation.
                         - "my_uncertain": Filters observations marked for validation and owned by the current user.
                         - "other_uncertain": Filters observations marked for validation but not owned by the current user.
        Returns:
            QuerySet: The filtered queryset based on the specified uncertainty criteria.
        """

        if value == "no_uncertain":
            return queryset.filter(Q(observations__isnull=True) | Q(observations__validation_requested=False))
        elif value == "uncertain":
            return queryset.filter(observations__validation_requested=True)
        elif value == "my_uncertain":
            return queryset.filter(observations__validation_requested=True, observations__owner=self.request.user)
        elif value == "other_uncertain":
            return queryset.filter(observations__validation_requested=True).exclude(observations__owner=self.request.user)

    class Meta:
        model = DataFile
        fields = GenericFilterMixIn.get_fields().copy()
        fields.update({
            'deployment__id': ['exact', 'in'],
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
            'favourite_of__id': ['exact', 'contains'],
        })


class DeviceModelFilter(GenericFilterMixIn, ExtraDataFilterMixIn):
    """
    A filter class for the `DeviceModel` model that combines functionality 
    from `GenericFilterMixIn` and `ExtraDataFilterMixIn`. This filter allows 
    querying `DeviceModel` instances based on various fields and lookup types.
    Attributes:
        Meta.model: Specifies the model associated with this filter (`DeviceModel`).
        Meta.fields: Defines the fields and their respective lookup types for filtering. 
                     Includes fields such as:
                     - `type`: Supports 'exact' and 'in' lookups.
                     - `type__name`: Supports 'exact', 'icontains', and 'in' lookups.
                     - `name`: Supports 'exact', 'icontains', and 'in' lookups.
    """

    class Meta:
        model = DeviceModel
        fields = GenericFilterMixIn.get_fields().copy()
        fields.update({
            'type': ['exact', 'in'],
            'type__name': ['exact', 'icontains', 'in'],
            'name': ['exact', 'icontains', 'in'],
        })
