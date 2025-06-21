from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import DataHandlerSerializer


@extend_schema(
    exclude=True
)
class DataHandlerViewSet(viewsets.ViewSet):

    serializer_class = DataHandlerSerializer
    permission_classes = [IsAuthenticated]

    @method_decorator(cache_page(60 * 60 * 2))
    def list(self, request):
        serializer = self.serializer_class(
            instance=settings.DATA_HANDLERS.data_handler_list, many=True)
        return Response(serializer.data)

    @method_decorator(cache_page(60 * 60 * 2))
    def retrieve(self, request, pk=None):
        try:
            data_handler = settings.DATA_HANDLERS.data_handler_list[int(pk)]
        except (IndexError, ValueError):
            return Response(status=404)

        serializer = self.serializer_class(data_handler)
        return Response(serializer.data)
