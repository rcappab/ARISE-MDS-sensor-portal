import os

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import timezone as djtimezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework_gis import filters as filters_gis
from utils.viewsets import OptionalPaginationViewSet
from django.db.models import Q
from .permissions import perms


from .filtersets import *
from .models import DataFile, DataType, Deployment, Device, Project, Site
from .serializers import *
from .file_handling_functions import create_file_objects
from .plotting_functions import get_all_file_metric_dicts


class AddOwnerViewSet(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CheckFormViewSet(viewsets.ModelViewSet):
    def get_serializer_context(self):
        context = super(CheckFormViewSet, self).get_serializer_context()

        context.update(
            {'form': 'multipart/form-data' in self.request.content_type})
        return context


class DeploymentViewSet(AddOwnerViewSet, CheckFormViewSet, OptionalPaginationViewSet):
    search_fields = ['deployment_device_ID',
                     'device__name', 'device__device_ID']
    ordering_fields = ordering = [
        'deployment_device_ID', 'created_on', 'device_type']
    queryset = Deployment.objects.all().distinct()
    filterset_class = DeploymentFilter
    filter_backends = viewsets.ModelViewSet.filter_backends + \
        [filters_gis.InBBoxFilter]

    def get_serializer_class(self):
        if 'geoJSON' in self.request.GET.keys():

            return DeploymentSerializer_GeoJSON
        else:
            return DeploymentSerializer

    @action(detail=True, methods=['get'])
    def metrics(self, request, pk=None):
        deployment = self.get_object()
        user = request.user
        data_files = perms['data_models.view_datafile'].filter(
            user, deployment.files.all())
        if not data_files.exists():
            return Response({}, status=status.HTTP_200_OK)
        file_metric_dicts = get_all_file_metric_dicts(data_files)
        return Response(file_metric_dicts, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        self.check_attachment(serializer)
        super(DeploymentViewSet, self).perform_update(serializer)

    def check_attachment(self, serializer):
        project_objects = serializer.validated_data.get('project')
        if project_objects is not None:
            for project_object in project_objects:
                if (not self.request.user.has_perm('data_models.change_project', project_object)) and\
                        (project_object.name != settings.GLOBAL_PROJECT_ID):
                    raise PermissionDenied(
                        f"You don't have permission to add a deployment to {project_object.project_ID}")
        device_object = serializer.validated_data.get('device')
        if device_object is not None:
            if not self.request.user.has_perm('data_models.change_device', device_object):
                raise PermissionDenied(
                    f"You don't have permission to deploy {device_object.device_ID}")


class ProjectViewSet(AddOwnerViewSet, OptionalPaginationViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all().distinct()
    filterset_class = ProjectFilter
    search_fields = ['project_ID', 'name', 'organization']

    @action(detail=True, methods=['get'])
    def metrics(self, request, pk=None):
        project = self.get_object()
        user = request.user
        data_files = perms['data_models.view_datafile'].filter(
            user, DataFile.objects.filter(deployment__project=project))
        if not data_files.exists():
            return Response({}, status=status.HTTP_200_OK)
        file_metric_dicts = get_all_file_metric_dicts(data_files)
        return Response(file_metric_dicts, status=status.HTTP_200_OK)


class DeviceViewSet(AddOwnerViewSet, OptionalPaginationViewSet):
    serializer_class = DeviceSerializer
    queryset = Device.objects.all().distinct()
    filterset_class = DeviceFilter
    search_fields = ['device_ID', 'name', 'model__name']

    @action(detail=True, methods=['get'])
    def metrics(self, request, pk=None):
        device = self.get_object()
        user = request.user
        data_files = perms['data_models.view_datafile'].filter(
            user, DataFile.objects.filter(deployment__device=device))
        if not data_files.exists():
            return Response({}, status=status.HTTP_200_OK)
        file_metric_dicts = get_all_file_metric_dicts(data_files)
        return Response(file_metric_dicts, status=status.HTTP_200_OK)


class DataFileViewSet(OptionalPaginationViewSet):

    queryset = DataFile.objects.all().distinct()
    filterset_class = DataFileFilter
    search_fields = ['file_name',
                     'deployment__deployment_device_ID',
                     'deployment__device__name',
                     'deployment__device__device_ID']

    @action(detail=True, methods=['post'], permission_classes=['data_models.view_datafile'])
    def favourite_file(self, request, pk=None):
        data_file = self.get_object()
        user = request.user
        if user:
            if data_file.favourite_of.all().filter(pk=user.pk).exists():
                data_file.favourite_of.remove(user)
            else:
                data_file.favourite_of.add(user)
            return Response({}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def perform_update(self, serializer):
        self.check_attachment(serializer)
        super(DataFileViewSet, self).perform_update(serializer)

    def check_attachment(self, serializer):
        deployment_object = serializer.validated_data.get(
            'deployment', serializer.instance.deployment)
        if not self.request.user.has_perm('data_models.change_deployment', deployment_object):
            raise PermissionDenied(f"You don't have permission to add a datafile"
                                   f" to {deployment_object.deployment_device_ID}")

    def get_serializer_class(self):
        if self.action == 'create':
            return DataFileUploadSerializer
        else:
            return DataFileSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        headers = self.get_success_headers(serializer.validated_data)

        instance = serializer.validated_data

        files = instance.get('files')
        recording_dt = instance.get('recording_dt')
        extra_data = instance.get('extra_data')
        deployment_object = instance.get('deployment_object')
        device_object = instance.get('device_object')
        data_types = instance.get('data_types')
        check_filename = instance.get('check_filename')

        uploaded_files, invalid_files, existing_files, status_code = create_file_objects(
            files, check_filename, recording_dt, extra_data, deployment_object, device_object, data_types, self.request.user)

        print([x.pk for x in uploaded_files])

        if status_code == status.HTTP_201_CREATED:
            returned_data = DataFileSerializer(data=uploaded_files, many=True)
            returned_data.is_valid()
            uploaded_files = returned_data.data

        return Response({"uploaded_files": uploaded_files, "invalid_files": invalid_files, "existing_files": existing_files},
                        status=status_code, headers=headers)


class SiteViewSet(viewsets.ReadOnlyModelViewSet, OptionalPaginationViewSet):
    serializer_class = SiteSerializer
    queryset = Site.objects.all().distinct()
    search_fields = ['name', 'short_name']


class DataTypeViewset(viewsets.ReadOnlyModelViewSet, OptionalPaginationViewSet):
    serializer_class = DataTypeSerializer
    queryset = DataType.objects.all().distinct()
    search_fields = ['name']
    filterset_class = DataTypeFilter
