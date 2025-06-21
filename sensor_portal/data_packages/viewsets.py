from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.mixins import (DestroyModelMixin, ListModelMixin,
                                   RetrieveModelMixin)
from utils.viewsets import AddOwnerViewSetMixIn, OptionalPaginationViewSetMixIn

from .models import DataPackage
from .serializers import DataPackageSerializer


@extend_schema(summary="Data packages",
               description="View details of data packages",
               tags=["Data packages"],
               methods=["get", "delete"],
               )
@extend_schema_view(
    list=extend_schema(summary="List data packages"),
    retrieve=extend_schema(summary="Get a single data package"),
    delete=extend_schema(summary="Delete data package")
)
class DataPackageViewSet(AddOwnerViewSetMixIn, OptionalPaginationViewSetMixIn):
    http_method_names = ['get', 'head', 'delete']
    search_fields = ['name']
    queryset = DataPackage.objects.all().distinct()
    serializer_class = DataPackageSerializer
