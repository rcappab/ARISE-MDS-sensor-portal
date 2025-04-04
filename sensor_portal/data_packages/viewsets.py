from rest_framework.mixins import (DestroyModelMixin, ListModelMixin,
                                   RetrieveModelMixin)
from utils.viewsets import AddOwnerViewSetMixIn, OptionalPaginationViewSetMixIn

from .models import DataPackage
from .serializers import DataPackageSerializer


class DataPackageViewSet(AddOwnerViewSetMixIn, OptionalPaginationViewSetMixIn):

    search_fields = ['name']
    queryset = DataPackage.objects.all().distinct()
    serializer_class = DataPackageSerializer
