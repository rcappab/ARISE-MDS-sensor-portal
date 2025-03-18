from django.db.models import QuerySet

from .models import Observation
from .serializers import ObservationSerializer


def create_metadata_dict(observation_objs: QuerySet[Observation]) -> dict:
    observation_dict = ObservationSerializer(observation_objs, many=True).data

    return observation_dict
