import os

from camtrap_dp_export.querysets import (get_ctdp_deployment_qs,
                                         get_ctdp_media_qs)
from camtrap_dp_export.serializers import (DataFileSerializerCTDP,
                                           DeploymentSerializerCTDP)
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import OperationalError, connection, transaction
from django.db.models import Q
from django.utils import timezone as djtimezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from observation_editor.models import Observation
from observation_editor.serializers import ObservationSerializer
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_gis import filters as filters_gis
from utils.viewsets import (AddOwnerViewSetMixIn, CheckAttachmentViewSetMixIn,
                            CheckFormViewSetMixIn,
                            OptionalPaginationViewSetMixIn)

from .file_handling_functions import create_file_objects
from .filtersets import (DataFileFilter, DataTypeFilter, DeploymentFilter,
                         DeviceFilter, DeviceModelFilter, ProjectFilter)
from .job_handling_functions import start_job_from_name
from .models import (DataFile, DataType, Deployment, Device, DeviceModel,
                     Project, Site)
from .permissions import perms
from .plotting_functions import get_all_file_metric_dicts
from .serializers import (DataFileCheckSerializer, DataFileSerializer,
                          DataFileUploadSerializer, DataTypeSerializer,
                          DeploymentSerializer, DeploymentSerializer_GeoJSON,
                          DeviceModelSerializer, DeviceSerializer,
                          GenericJobSerializer, ProjectSerializer,
                          SiteSerializer)


class DeploymentViewSet(CheckAttachmentViewSetMixIn, AddOwnerViewSetMixIn, CheckFormViewSetMixIn, OptionalPaginationViewSetMixIn):
    search_fields = ['deployment_device_ID',
                     'device__name', 'device__device_ID', 'extra_data']
    ordering_fields = ordering = [
        'deployment_device_ID', 'created_on', 'device_type']
    queryset = Deployment.objects.all().distinct()
    filterset_class = DeploymentFilter
    filter_backends = viewsets.ModelViewSet.filter_backends + \
        [filters_gis.InBBoxFilter]

    @action(detail=False, methods=['post'])
    def ids_count(self, request, *args, **kwargs):
        queryset = Deployment.objects.filter(pk__in=request.data.get("ids"))
        return Response(queryset.file_count(), status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def queryset_count(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return Response(queryset.file_count(), status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path=r'start_job/(?P<job_name>\w+)')
    def start_job(self, request, job_name, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())

        user_pk = request.user.pk

        if not (obj_pks := request.data.get("ids")):
            obj_pks = list(queryset.values_list('pk', flat=True))
        else:
            request.data.pop("ids")

        job_args = request.data
        success, detail, job_status = start_job_from_name(
            job_name, "deployment", obj_pks, job_args, user_pk)

        return Response({"detail": detail}, status=job_status)

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
    queryset = Project.objects.all().distinct().exclude(
        name=settings.GLOBAL_PROJECT_ID)
    filterset_class = ProjectFilter
    search_fields = ['project_ID', 'name', 'organization']

    @action(detail=False, methods=['post'])
    def ids_count(self, request, *args, **kwargs):
        queryset = Project.objects.filter(pk__in=request.data.get("ids"))
        return Response(queryset.file_count(), status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def queryset_count(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return Response(queryset.file_count(), status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path=r'start_job/(?P<job_name>\w+)')
    def start_job(self, request, job_name, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())

        user_pk = request.user.pk

        if not (obj_pks := request.data.get("ids")):
            obj_pks = list(queryset.values_list('pk', flat=True))
        else:
            request.data.pop("ids")

        job_args = request.data
        success, detail, job_status = start_job_from_name(
            job_name, "project", obj_pks, job_args, user_pk)

        return Response({"detail": detail}, status=job_status)

    @action(detail=True, methods=['get'])
    def species_list(self, request, pk=None):
        project = self.get_object()
        user = request.user
        data_files = perms['data_models.view_datafile'].filter(
            user, DataFile.objects.filter(deployment__project=project))
        if not data_files.exists():
            return Response({}, status=status.HTTP_200_OK)
        species_list = list(data_files.values_list(
            "observations__taxon__species_name", flat=True).distinct())
        return Response(species_list, status=status.HTTP_200_OK)

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

    @action(detail=False, methods=['post'])
    def ids_count(self, request, *args, **kwargs):
        queryset = Device.objects.filter(pk__in=request.data.get("ids"))
        return Response(queryset.file_count(), status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def queryset_count(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return Response(queryset.file_count(), status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path=r'start_job/(?P<job_name>\w+)')
    def start_job(self, request, job_name, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())

        user_pk = request.user.pk

        if not (obj_pks := request.data.get("ids")):
            obj_pks = list(queryset.values_list('pk', flat=True))
        else:
            request.data.pop("ids")

        job_args = request.data
        success, detail, job_status = start_job_from_name(
            job_name, "device", obj_pks, job_args, user_pk)

        return Response({"detail": detail}, status=job_status)

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

    search_fields = ['=tag',
                     'file_name',
                     'observations__taxon__species_name',
                     'observations__taxon__species_common_name']

    def get_queryset(self):
        qs = DataFile.objects.prefetch_related(
            "observations__taxon").all().distinct()
        if 'CTDP' in self.request.GET.keys():
            qs = get_ctdp_media_qs(qs)
        return qs

    @action(detail=False, methods=['post'])
    def check_existing(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = DataFileCheckSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        if (original_names := serializer.validated_data.get('original_names')):
            existing_names = queryset.filter(
                original_name__in=original_names).values_list('original_name', flat=True)
            print(existing_names)
            missing_names = [
                x for x in original_names if x not in existing_names]
        elif (file_names := serializer.validated_data.get('file_names')):
            existing_names = queryset.filter(
                file_name__in=file_names).values_list('file_name', flat=True)
            missing_names = [
                x for x in original_names if x not in existing_names]
        else:
            return Response({"detail": "Either 'original_names' or 'file_names' must be provided."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(missing_names, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def ids_count(self, request, *args, **kwargs):
        queryset = DataFile.objects.filter(pk__in=request.data.get("ids"))
        return Response(queryset.file_count(), status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def queryset_count(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return Response(queryset.file_count(), status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path=r'start_job/(?P<job_name>\w+)')
    def start_job(self, request, job_name, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())

        user_pk = request.user.pk

        if not (obj_pks := request.data.get("ids")):
            obj_pks = list(queryset.values_list('pk', flat=True))
        else:
            request.data.pop("ids")

        job_args = request.data
        success, detail, job_status = start_job_from_name(
            job_name, "datafile", obj_pks, job_args, user_pk)

        return Response({"detail": detail}, status=job_status)

    @action(detail=True, methods=['get'])
    def observations(self, request, pk=None):
        data_file = self.get_object()
        observation_qs = Observation.objects.filter(
            data_files=data_file).distinct()
        observation_serializer = ObservationSerializer(
            observation_qs, many=True, context={'request': request})
        return Response(observation_serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
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

        multipart = 'HTTP_CONTENT_RANGE' in request.META

        with transaction.atomic(), connection.cursor() as cursor:
            # Remove db limits during this function.
            cursor.execute('SET LOCAL statement_timeout TO 0;')
            uploaded_files, invalid_files, existing_files, status_code = create_file_objects(
                files, check_filename, recording_dt, extra_data, deployment_object, device_object,
                data_types, self.request.user, multipart)

        print(
            f"Uploaded files: {uploaded_files}, Invalid files: {invalid_files}, Existing files: {existing_files}, Status code: {status_code}")

        if len(uploaded_files) > 0:
            returned_data = DataFileSerializer(data=uploaded_files, many=True)
            returned_data.is_valid()
            uploaded_files = returned_data.data

        return Response({"uploaded_files": uploaded_files, "invalid_files": invalid_files, "existing_files": existing_files},
                        status=status_code, headers=headers)


class SiteViewSet(viewsets.ReadOnlyModelViewSet, OptionalPaginationViewSetMixIn):
    serializer_class = SiteSerializer
    queryset = Site.objects.all().distinct()
    search_fields = ['name', 'short_name']

    @method_decorator(cache_page(60 * 60 * 2))
    @method_decorator(vary_on_cookie)
    def list(self, request):
        return super().list(request)


class DataTypeViewSet(viewsets.ReadOnlyModelViewSet, OptionalPaginationViewSetMixIn):
    serializer_class = DataTypeSerializer
    queryset = DataType.objects.all().distinct()
    search_fields = ['name']
    filterset_class = DataTypeFilter

    @method_decorator(cache_page(60 * 60 * 2))
    def list(self, request):
        return super().list(request)


class DeviceModelViewSet(viewsets.ReadOnlyModelViewSet, OptionalPaginationViewSetMixIn):
    serializer_class = DeviceModelSerializer
    queryset = DeviceModel.objects.all().distinct()
    search_fields = ['name']
    filterset_class = DeviceModelFilter

    @method_decorator(cache_page(60 * 60 * 2))
    def list(self, request):
        return super().list(request)


class GenericJobViewSet(viewsets.ViewSet):
    # Required for the Browsable API renderer to have a nice form.
    serializer_class = GenericJobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        job_list = settings.GENERIC_JOBS.values()
        if not user.is_staff:
            job_list = [x for x in job_list if not x["admin_only"]]

        data_type = self.request.query_params.get('data_type')
        if data_type is not None:
            job_list = [x for x in job_list if x["data_type"] == data_type]
        return job_list

    @method_decorator(cache_page(60 * 60 * 2))
    @method_decorator(vary_on_cookie)
    def list(self, request):

        serializer = self.serializer_class(
            instance=self.get_queryset(), many=True)

        return Response(serializer.data)

    @method_decorator(cache_page(60 * 60 * 2))
    @method_decorator(vary_on_cookie)
    def retrieve(self, request, pk=None):
        try:
            job_dict = list(settings.GENERIC_JOBS.values())[int(pk)]
        except (IndexError, ValueError):
            return Response(status=404)

        serializer = self.serializer_class(job_dict)
        return Response(serializer.data)
