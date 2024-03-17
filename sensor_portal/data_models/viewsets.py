from .models import *
from .serializers import *
from rest_framework import viewsets
import django_filters.rest_framework
from rest_framework.authentication import TokenAuthentication, SessionAuthentication


class DeploymentViewset(viewsets.ModelViewSet):
    queryset = Deployment.objects.all()

    def get_serializer_class(self):
        print(self.request.GET)
        if 'geoJSON' in self.request.GET.keys():
            return DeploymentSerializer_GeoJSON
        else:
            return DeploymentSerializer


class ProjectViewset(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()


class DeviceViewset(viewsets.ModelViewSet):
    serializer_class = DeviceSerializer
    queryset = Device.objects.all()

from rest_framework import status
from rest_framework.response import Response

class DataFileViewset(viewsets.ModelViewSet):
    serializer_class = DataFileSerializer
    queryset = DataFile.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return DataFileUploadSerializer
        else:
            return DataFileSerializer


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        headers = self.get_success_headers(serializer.validated_data)
        response = Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


        if response.status_code!=201:
            return response
        else:
            instance = response.validated_data
            #  check deployment availability
            #  write to disk

            #return a job submitted response
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)





