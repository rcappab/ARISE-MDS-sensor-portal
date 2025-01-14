import os

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import timezone as djtimezone
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework_gis import filters as filters_gis
from utils.general import check_dt, get_new_name, handle_uploaded_file
from utils.viewsets import OptionalPaginationViewSet

from .filtersets import *
from .models import DataFile, DataType, Deployment, Device, Project, Site
from .serializers import *


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

    def perform_create(self, serializer):
        self.check_attachment(serializer)
        super(DeploymentViewSet, self).perform_create(serializer)

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


class DeviceViewSet(AddOwnerViewSet, OptionalPaginationViewSet):
    serializer_class = DeviceSerializer
    queryset = Device.objects.all().distinct()
    filterset_class = DeviceFilter
    search_fields = ['device_ID', 'name', 'model__name']


class DataFileViewSet(OptionalPaginationViewSet):

    queryset = DataFile.objects.all().distinct()
    filterset_class = DataFileFilter
    search_fields = ['file_name',
                     'deployment__deployment_device_ID',
                     'deployment__device__name',
                     'deployment__device__device_ID']

    def perform_update(self, serializer):
        self.check_attachment(serializer)
        super(DataFileViewSet, self).perform_update(serializer)

    def check_attachment(self, deployment_object):
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

        returned_data = DataFileSerializer(data=uploaded_files, many=True)
        returned_data.is_valid()

        return Response({"uploaded_files": returned_data.data, "invalid_files": invalid_files, "existing_files": existing_files},
                        status=status_code, headers=headers)

    def create_file_objects(files, check_filename=False, recording_dt=None, extra_data=None, deployment_object=None,
                            device_object=None, data_types=None, request_user=None):

        if extra_data is None:
            extra_data = [{}]

        if recording_dt is None:
            recording_dt = [get_image_recording_dt(x) for x in files]

        invalid_files = []
        existing_files = []
        uploaded_files = []
        upload_dt = str(djtimezone.now())

        if check_filename:
            #  check if the original name already exists in the database
            filenames = [x.name for x in files]
            db_filenames = list(
                DataFile.objects.filter(original_name__in=filenames).values_list('original_name', flat=True))
            not_duplicated = [x not in db_filenames for x in filenames]
            files = [x for x, y in zip(files, not_duplicated) if y]
            existing_files += [f"{x} - already in database" for x,
                               y in zip(filenames, not_duplicated) if not y]
            if len(files) == 0:
                return (uploaded_files, invalid_files, existing_files, status.HTTP_200_OK)

            if len(recording_dt) > 1:
                recording_dt = [x for x, y in zip(
                    recording_dt, not_duplicated) if y]
            if len(extra_data) > 1:
                extra_data = [x for x, y in zip(
                    extra_data, not_duplicated) if y]
            if data_types is not None:
                if len(data_types) > 1:
                    data_types = [x for x, y in zip(
                        data_types, not_duplicated) if y]

        if deployment_object:
            if request_user:
                if not request_user.has_perm('data_models.change_deployment', deployment_object):
                    invalid_files += [
                        f"{x.name} - Not allowed to attach files to this deployment" for x in files]
                    return (uploaded_files, invalid_files, existing_files, status.HTTP_403_FORBIDDEN)

            file_valid = deployment_object.check_dates(recording_dt)
            deployment_objects = list(deployment_object)

        elif device_object:
            deployment_objects = [device_object.deployment_from_date(
                x) for x in recording_dt]
            file_valid = [x is not None for x in deployment_objects]
            # Filter deployments to only valids
            deployment_objects = [
                x for x in deployment_objects if x is not None]

        #  split off invalid  files
        invalid_files += [f"{x.name} - no suitable deployment found" for x,
                          y in zip(files, file_valid) if not y]
        files = [x for x, y in zip(files, file_valid) if y]

        if len(files) == 0:
            return (uploaded_files, invalid_files, existing_files, status.HTTP_400_BAD_REQUEST)

        if len(recording_dt) > 1:
            recording_dt = [x for x, y in zip(
                recording_dt, file_valid) if y]
        if len(extra_data) > 1:
            extra_info = [x for x, y in zip(extra_data, file_valid) if y]
        if data_types is not None:
            if len(data_types) > 1:
                data_types = [x for x, y in zip(
                    data_types, file_valid) if y]

        all_new_objects = []
        for i in range(len(files)):
            file = files[i]
            if len(deployment_objects) > 1:
                file_deployment = deployment_objects[i]
            else:
                file_deployment = deployment_objects[0]

            if len(recording_dt) > 1:
                file_recording_dt = recording_dt[i]
            else:
                file_recording_dt = recording_dt[0]

            # localise recording_dt to deployment tz or server tz
            file_recording_dt = check_dt(
                file_recording_dt, file_deployment.time_zone)

            if len(extra_info) > 1:
                file_extra_data = extra_data[i]
            else:
                file_extra_data = extra_data[0]

            if data_types is None:
                file_data_type = file_deployment.device_type
            else:
                if len(data_types) > 1:
                    file_data_type = data_types[i]
                else:
                    file_data_type = data_types[0]

            file_local_path = os.path.join(
                settings.FILE_STORAGE_ROOT, file_data_type.name)
            file_path = os.path.join(
                file_deployment.deployment_device_ID, str(upload_dt.date()))
            filename = file.name
            file_extension = os.path.splitext(filename)[1]
            new_file_name = get_new_name(file_deployment,
                                         file_recording_dt,
                                         file_local_path,
                                         file_path
                                         )

            file_size = os.fstat(file.fileno()).st_size

            file_fullpath = os.path.join(
                file_local_path, file_path, f"{new_file_name}{file_extension}")

            new_datafile_obj = DataFile(
                deployment=file_deployment,
                file_type=file_data_type,
                file_name=new_file_name,
                original_name=filename,
                file_format=file_extension,
                upload_dt=upload_dt,
                recording_dt=file_recording_dt,
                path=file_path,
                local_path=file_local_path,
                file_size=file_size,
                extra_data=file_extra_data
            )

            handle_uploaded_file(file, file_fullpath)

            new_datafile_obj.set_file_url()
            all_new_objects.append(new_datafile_obj)

        # probably shift all this to an async job
        uploaded_files = DataFile.objects.bulk_create(all_new_objects, update_conflicts=True, update_fields=[
            "extra_data"], unique_fields=["file_name"])
        for deployment in deployment_objects:
            deployment.set_last_file()
        return (uploaded_files, invalid_files, existing_files, status.HTTP_201_CREATED)


class SiteViewSet(viewsets.ReadOnlyModelViewSet, OptionalPaginationViewSet):
    serializer_class = SiteSerializer
    queryset = Site.objects.all().distinct()
    search_fields = ['name', 'short_name']


class DataTypeViewset(viewsets.ReadOnlyModelViewSet, OptionalPaginationViewSet):
    serializer_class = DataTypeSerializer
    queryset = DataType.objects.all().distinct()
    search_fields = ['name']
