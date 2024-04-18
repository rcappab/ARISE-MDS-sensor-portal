from rest_framework import viewsets
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.response import Response
from utils.viewsets import OptionalPaginationViewSet
from utils.general import handle_uploaded_file, get_new_name
from django.conf import settings
from rest_framework_gis import filters as filters_gis


from .serializers import *
from .filtersets import *



class AddOwnerViewSet(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class DeploymentViewSet(AddOwnerViewSet, OptionalPaginationViewSet):
    search_fields = ['deployment_deviceID', 'device__name', 'device__deviceID']
    queryset = Deployment.objects.all()
    filterset_class = DeploymentFilter
    filter_backends = viewsets.ModelViewSet.filter_backends + [filters_gis.InBBoxFilter]

    def get_serializer_class(self):
        print(self.request.GET)
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
                if not self.request.user.has_perm('data_models.change_project', project_object):
                    raise PermissionDenied(
                        f"You don't have permission to add a deployment to {project_object.projectID}")
        device_object = serializer.validated_data.get('device')
        if not self.request.user.has_perm('data_models.change_device', device_object):
            raise PermissionDenied(f"You don't have permission to deploy {device_object.deviceID}")


class ProjectViewSet(AddOwnerViewSet, OptionalPaginationViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    filterset_class = ProjectFilter
    search_fields = ['projectID', 'projectName', 'organizationName']


class DeviceViewSet(AddOwnerViewSet, OptionalPaginationViewSet):
    serializer_class = DeviceSerializer
    queryset = Device.objects.all()
    filterset_class = DeviceFilter
    search_fields = ['deviceID', 'name', 'model', 'make']

class DataFileViewSet(OptionalPaginationViewSet):
    serializer_class = DataFileSerializer
    queryset = DataFile.objects.all()
    filterset_class = DataFileFilter
    search_fields = ['file_name',
                     'deployment__deployment_deviceID',
                     'deployment__device__name',
                     'deployment__device__deviceID']

    def perform_update(self, serializer):
        self.check_attachment(serializer)
        super(DataFileViewSet, self).perform_update(serializer)

    def check_attachment(self, serializer):
        deployment_object = serializer.validated_data.get('deployment')
        if not self.request.user.has_perm('data_models.change_deployment', deployment_object):
            raise PermissionDenied(f"You don't have permission to add a datafile"
                                   f" to {deployment_object.deployment_deviceID}")

    def get_serializer_class(self):
        if self.action == 'create':
            return DataFileUploadSerializer
        else:
            return DataFileSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        headers = self.get_success_headers(serializer.validated_data)
        upload_date = str(djtimezone.now().date())
        instance = serializer.validated_data

        files = instance.get('files')
        recording_dt = instance.get('recording_dt')
        extra_info = instance.get('extra_info', [{}])
        deployment = instance.get('deployment')
        device = instance.get('device')
        data_types = instance.get('data_types')

        invalid_files = []

        if instance.get('check_filename'):
            #  check if the original name already exists in the database
            filenames = [x.name for x in files]
            db_filenames = list(
                DataFile.objects.filter(original_name__in=filenames).values_list('original_name', flat=True))
            not_duplicated = [x not in db_filenames for x in filenames]
            files = [x for x, y in zip(files, not_duplicated) if y]
            invalid_files += [f"{x} - already in database" for x, y in zip(filenames, not_duplicated) if not y]
            if len(files)==0:
                return Response({"uploaded_files": [], "invalid_files": invalid_files},
                                status=status.HTTP_201_CREATED, headers=headers)
            if len(recording_dt) > 1:
                recording_dt = [x for x, y in zip(recording_dt, not_duplicated) if y]
            if len(extra_info) > 1:
                extra_info = [x for x, y in zip(extra_info, not_duplicated) if y]
            if data_types is not None:
                if len(data_types) > 1:
                    data_types = [x for x, y in zip(data_types, not_duplicated) if y]

        if deployment:
            deployment_pk = None
            if deployment.isnumeric():
                deployment_pk = int(deployment)
            try:
                deployment_object = Deployment.objects.filter(Q(Q(deployment_deviceID=deployment) |
                                                                Q(pk=deployment_pk)))
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Incorrect deployment")

            self.check_attachment(serializer)

            valid_files = deployment_object.check_dates(recording_dt)
            if all([not x for x in valid_files]):
                serializers.ValidationError(f"deployment {deployment} is invalid for all files")
            deployment_objects = list(deployment_object)
        else:

            device_pk = None
            if device.isnumeric():
                device_pk = int(device)
            try:
                device_object = Device.objects.get(Q(Q(deviceID=device) | Q(pk=device_pk)))
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Incorrect device")

            deployment_objects = [device_object.deployment_from_date(x, request.user) for x in recording_dt]
            print(deployment_objects)
            valid_files = [x is not None for x in deployment_objects]
            print(valid_files)
            if all([not x for x in valid_files]):
                raise serializers.ValidationError(f"No deployments found in device {device_object.deviceID}")
            # Filter to only valids
            deployment_objects = [x for x in deployment_objects if x is not None]

        #  split off invalid  files
        invalid_files += [f"{x.name} - no suitable deployment found" for x, y in zip(files, valid_files) if not y]
        files = [x for x, y in zip(files, valid_files) if y]
        if len(recording_dt) > 1:
            recording_dt = [x for x, y in zip(recording_dt, valid_files) if y]
        if len(extra_info) > 1:
            extra_info = [x for x, y in zip(extra_info, valid_files) if y]
        if data_types is not None:
            if len(data_types) > 1:
                data_types = [x for x, y in zip(data_types, valid_files) if y]

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

            if len(extra_info) > 1:
                file_extra_info = extra_info[i]
            else:
                file_extra_info = extra_info[0]

            if data_types is None:
                file_data_type = file_deployment.device_type
            else:
                if len(data_types) > 1:
                    file_data_type = data_types[i]
                else:
                    file_data_type = data_types[0]

            file_local_path = os.path.join(settings.FILE_STORAGE_ROOT, file_data_type.name)
            file_path = os.path.join(file_deployment.deployment_deviceID, upload_date)
            filename = file.name
            file_extension = os.path.splitext(filename)[1]
            new_file_name = get_new_name(file_deployment,
                                         file_recording_dt,
                                         file_local_path,
                                         file_path
                                         )
            file_size = os.fstat(file.fileno()).st_size
            file_fullpath = os.path.join(file_local_path, file_path, f"{new_file_name}{file_extension}")
            handle_uploaded_file(file, file_fullpath)
            new_datafile_obj = DataFile(
                deployment=file_deployment,
                file_type=file_data_type,
                file_name=new_file_name,
                original_name=filename,
                file_format=file_extension,
                upload_date=upload_date,
                recording_dt=file_recording_dt,
                path=file_path,
                local_path=file_local_path,
                file_size=file_size,
                extra_info=file_extra_info
            )
            new_datafile_obj.set_file_url()
            all_new_objects.append(new_datafile_obj)

        # probably shift all this to an async job
        DataFile.objects.bulk_create(all_new_objects)
        returned_data = DataFileSerializer(data=all_new_objects, many=True)
        returned_data.is_valid()
        for deployment in deployment_objects:
            deployment.set_last_file()
        return Response({"uploaded_files": returned_data.data, "invalid_files": invalid_files},
                        status=status.HTTP_201_CREATED, headers=headers)

class SiteViewSet(viewsets.ReadOnlyModelViewSet, OptionalPaginationViewSet):
    serializer_class = SiteSerializer
    queryset = Site.objects.all()
    search_fields = ['name','short_name']

class DataTypeViewset(viewsets.ReadOnlyModelViewSet, OptionalPaginationViewSet):
    serializer_class = DataTypeSerializer
    queryset = DataType.objects.all()
    search_fields = ['name']







