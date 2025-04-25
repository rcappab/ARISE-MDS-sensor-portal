from django.conf import settings
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import DataHandlerSerializer


class DataHandlerViewSet(viewsets.ViewSet):
    # Required for the Browsable API renderer to have a nice form.
    serializer_class = DataHandlerSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        serializer = self.serializer_class(
            instance=settings.DATA_HANDLERS.data_handler_list, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            data_handler = settings.DATA_HANDLERS.data_handler_list[int(pk)]
        except (IndexError, ValueError):
            return Response(status=404)

        serializer = self.serializer_class(data_handler)
        return Response(serializer.data)
