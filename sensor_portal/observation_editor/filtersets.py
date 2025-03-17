import django_filters.rest_framework
from utils.filtersets import ExtraDataFilterMixIn, GenericFilterMixIn

from .models import Observation


class ObservationFilter(GenericFilterMixIn, ExtraDataFilterMixIn):
    class Meta:
        model = Observation
        fields = GenericFilterMixIn.get_fields().copy()
        fields.update({
            'data_files': ['exact']
        })
