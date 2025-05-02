from django_filters import NumberFilter
from utils.filtersets import GenericFilterMixIn

from .models import DataStorageInput


class DataStorageFilter(GenericFilterMixIn):
    project_id = NumberFilter(
        field_name='linked_projects', label='Project ID', lookup_expr='exact')

    class Meta:
        model = DataStorageInput
        fields = GenericFilterMixIn.get_fields().copy()
