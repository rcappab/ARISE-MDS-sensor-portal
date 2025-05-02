from external_storage_import.serializers import DataStorageInputSerializer
from utils.viewsets import AddOwnerViewSetMixIn

from .filtersets import DataStorageFilter
from .models import DataStorageInput


class DataStorageInputViewSet(AddOwnerViewSetMixIn):
    serializer_class = DataStorageInputSerializer
    queryset = DataStorageInput.objects.all().distinct()
    search_fields = ['name']
    filterset_class = DataStorageFilter
