import os

from camtrap_dp_export.querysets import (get_ctdp_deployment_qs,
                                         get_ctdp_media_qs)
from camtrap_dp_export.serializers import (DataFileSerializerCTDP,
                                           DeploymentSerializerCTDP)
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import timezone as djtimezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework_gis import filters as filters_gis
from utils.viewsets import (AddOwnerViewSetMixIn, CheckAttachmentViewSetMixIn,
                            CheckFormViewSetMixIn,
                            OptionalPaginationViewSetMixIn)

from .file_handling_functions import create_file_objects
from .filtersets import *
from .job_handling_functions import start_job_from_name
from .models import (DataFile, DataType, Deployment, Device, DeviceModel,
                     Project, Site)
from .permissions import perms
from .plotting_functions import get_all_file_metric_dicts
from .serializers import (DataFileSerializer, DataFileUploadSerializer,
                          DataTypeSerializer, DeploymentSerializer,
                          DeploymentSerializer_GeoJSON, DeviceModelSerializer,
                          DeviceSerializer, ProjectSerializer, SiteSerializer)


class DeploymentViewSet(CheckAttachmentViewSetMixIn, AddOwnerViewSetMixIn, CheckFormViewSetMixIn, OptionalPaginationViewSetMixIn):
    search_fields = ['deployment_device_ID',
                     'device__name', 'device__device_ID']
    ordering_fields = ordering = [
        'deployment_device_ID', 'created_on', 'device_type']
    queryset = Deployment.objects.all().distinct()
    filterset_class = DeploymentFilter
    filter_backends = viewsets.ModelViewSet.filter_backends + \
        [filters_gis.InBBoxFilter]

    def get_queryset(self):
        qs = Deployment.objects.all().distinct()
        if 'CTDP' in self.request.GET.keys():
            qs = get_ctdp_deployment_qs(qs)
        return qs

    def get_serializer_class(self):
        if 'geoJSON' in self.request.GET.keys():
            return DeploymentSerializer_GeoJSON
        elif 'CTDP' in self.request.GET.keys():
            return DeploymentSerializerCTDP
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


class ProjectViewSet(AddOwnerViewSetMixIn, OptionalPaginationViewSetMixIn):
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
        file_metric_dicts = get_all_file_metric_dicts(data_files, False)
        return Response(file_metric_dicts, status=status.HTTP_200_OK)


class DeviceViewSet(AddOwnerViewSetMixIn, OptionalPaginationViewSetMixIn):
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


class DataFileViewSet(CheckAttachmentViewSetMixIn, OptionalPaginationViewSetMixIn):

    filterset_class = DataFileFilter

    search_fields = ['file_name',
                     'deployment__deployment_device_ID',
                     'deployment__device__name',
                     'deployment__device__device_ID',
                     '=tag']

    def get_queryset(self):
        qs = DataFile.objects.all().distinct()
        if 'CTDP' in self.request.GET.keys():
            qs = get_ctdp_media_qs(qs)
        return qs

    @action(detail=False, methods=['get'])
    def queryset_count(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return Response(queryset.file_count(), status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path=r'start_job/(?P<job_name>\w+)')
    def start_job(self, request, job_name, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if (job_size := queryset.count()) > settings.MAX_JOB_SIZE:
            return Response({"detail":
                             f"Requested job of {job_size} exceeds maximum job size of {settings.MAX_JOB_SIZE}"},
                            status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

        print(request.data)

        user_pk = request.user.pk
        file_pks = list(queryset.values_list('pk', flat=True))
        job_args = request.data
        start_job_from_name(job_name, user_pk, file_pks, job_args)

        return Response({"detail": f"{job_name} submitted"}, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['post'], permission_classes=['data_models.view_datafile'])
    def favourite_file(self, request):
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
            if 'CTDP' in self.request.GET.keys():
                return DataFileSerializerCTDP
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


class SiteViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SiteSerializer
    queryset = Site.objects.all().distinct()
    search_fields = ['name', 'short_name']


class DataTypeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DataTypeSerializer
    queryset = DataType.objects.all().distinct()
    search_fields = ['name']
    filterset_class = DataTypeFilter


class DeviceModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DeviceModelSerializer
    queryset = DeviceModel.objects.all().distinct()
    search_fields = ['name']
