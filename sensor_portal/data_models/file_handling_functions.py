import itertools
import os
from datetime import datetime as dt

from celery import chain
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone as djtimezone
from rest_framework import status
from utils.general import convert_unit, get_md5

from sensor_portal.celery import app

from .general_functions import check_dt


def create_file_objects(files, check_filename=False, recording_dt=None, extra_data=None, deployment_object=None,
                        device_object=None, data_types=None, request_user=None, multipart=False, verbose=False):
    from data_models.models import DataFile, DataType, ProjectJob

    invalid_files = []
    existing_files = []
    uploaded_files = []
    if extra_data is None:
        extra_data = [{}]

    if verbose:
        print("Initial files:", files)
        print("Device object:", device_object)
        print("Deployment object:", deployment_object)
        print("Recording datetime:", recording_dt)
        print("Extra data:", extra_data)
        print("Data types:", data_types)
        print("Request user:", request_user)

    upload_dt = djtimezone.now()

    if check_filename or multipart:
        if verbose:
            print("Checking filenames or handling multipart upload...")

        #  check if the original name already exists in the database
        filenames = [x.name for x in files]

        if multipart:
            if verbose:
                print("Handling multipart upload...")

            if len(filenames) > 1:
                invalid_files += [{x: {"message": "Multipart file upload expects a single file chunk", "status": 400}} for x,
                                  in filenames]
                return (uploaded_files, invalid_files, existing_files, status.HTTP_400_BAD_REQUEST)

            multipart_obj = None
            multipart_checksum = None

            existing_multipart_files = DataFile.objects.filter(
                original_name__in=filenames, extra_data__md5_checksum__isnull=True)
            if device_object:
                existing_multipart_files = existing_multipart_files.filter(
                    deployment__device=device_object)

            if deployment_object:
                existing_multipart_files = existing_multipart_files.filter(
                    deployment=deployment_object)

            if existing_multipart_files.exists():
                if verbose:
                    print("Found existing multipart object in the database.")

                multipart_obj = existing_multipart_files.first()

                recording_dt = [multipart_obj.recording_dt]
                deployment_object = multipart_obj.deployment
                device_object = deployment_object.device

                multipart_checksum = extra_data[0].get("md5_checksum")

        else:
            if verbose:
                print("Checking for duplicate filenames in the database...")

            db_filenames = list(
                DataFile.objects.filter(original_name__in=filenames).values_list('original_name', flat=True))

            not_duplicated = [x not in db_filenames for x in filenames]
            files = [x for x, y in zip(files, not_duplicated) if y]
            existing_files += [{x: {"message": "Already in database", "status": 200}} for x,
                               y in zip(filenames, not_duplicated) if not y]

            if len(files) == 0:
                if verbose:
                    print("All files are already in the database.")
                return (uploaded_files, invalid_files, existing_files, status.HTTP_200_OK)

        if recording_dt and len(recording_dt) > 1:
            recording_dt = [x for x, y in zip(
                recording_dt, not_duplicated) if y]
        if len(extra_data) > 1:
            extra_data = [x for x, y in zip(
                extra_data, not_duplicated) if y]
        if data_types is not None:
            if len(data_types) > 1:
                data_types = [x for x, y in zip(
                    data_types, not_duplicated) if y]

    if device_object is None and deployment_object:
        if verbose:
            print("Setting device_object from deployment_object...")
        device_object = deployment_object.device

    handler_tasks = None

    if device_object:
        if verbose:
            print("Processing files with device_object...")

        device_model_object = device_object.model
        data_handlers = settings.DATA_HANDLERS

        data_handler = data_handlers.get_handler(
            device_model_object.type.name, device_model_object.name)

        if data_handler is not None:
            if verbose:
                print(f"Using data handler for {device_model_object.name}...")

            valid_files = data_handler.get_valid_files(files)

            if len(valid_files) == 0:
                if verbose:
                    print("No valid files found for the device model.")
                invalid_files += [{x.name: {"message": f"Invalid file type for {device_model_object.name}", "status": 400}}
                                  for x in files]
                return (uploaded_files, invalid_files, existing_files, status.HTTP_400_BAD_REQUEST)
            else:
                valid_files_bool = [x in valid_files for x in files]
                invalid_files += [{x.name: {"message": f"Invalid file type for {device_model_object.name}", "status": 400}}
                                  for x, y in zip(files, valid_files_bool) if not y]

                files = valid_files
                if recording_dt is not None and len(recording_dt) > 1:
                    recording_dt = [x for x, y in zip(
                        recording_dt, valid_files_bool) if y]
                if extra_data and len(extra_data) > 1:
                    extra_data = [x for x, y in zip(
                        extra_data, valid_files_bool) if y]

            new_recording_dt = []
            new_extra_data = []
            new_data_types = []
            new_tasks = []

            for i in range(len(files)):
                if len(extra_data) > 1:
                    file_extra_data = extra_data[i]
                else:
                    file_extra_data = extra_data[0]

                if recording_dt is None:
                    file_recording_dt = recording_dt
                elif len(recording_dt) > 1:
                    file_recording_dt = recording_dt[i]
                else:
                    file_recording_dt = recording_dt[0]
                file = files[i]

                if verbose:
                    print(f"Handling file {file.name} with data handler...")

                new_file_recording_dt, new_file_extra_data, new_file_data_type, new_file_task = \
                    data_handler.handle_file(
                        file,
                        file_recording_dt,
                        file_extra_data,
                        device_model_object.type.name
                    )

                new_recording_dt.append(new_file_recording_dt)
                new_extra_data.append(new_file_extra_data)
                new_data_types.append(new_file_data_type)
                new_tasks.append(new_file_task)

            recording_dt = new_recording_dt
            extra_data = new_extra_data
            data_types = new_data_types
            handler_tasks = new_tasks

    else:
        if verbose:
            print("No linked device found for the files.")
        invalid_files += [{x.name: {"message": "No linked device", "status": 400}}
                          for x in files]
        return (uploaded_files, invalid_files, existing_files, status.HTTP_400_BAD_REQUEST)

    if all([x is None for x in recording_dt]):
        invalid_files += [{x.name: {"message": "Unable to extract recording date time", "status": 400}}
                          for x in files]
        return (uploaded_files, invalid_files, existing_files, status.HTTP_400_BAD_REQUEST)

    if deployment_object:
        if verbose:
            print("Checking permissions for deployment_object...")
        if request_user:
            if not request_user.has_perm('data_models.change_deployment', deployment_object):
                if verbose:
                    print(
                        f"User does not have permission to attach files to {deployment_object.deployment_device_ID}.")
                invalid_files += [
                    {x.name: {
                        "message": f"Not allowed to attach files to {deployment_object.deployment_device_ID}",
                        "status": 403}}
                    for x in files]
                return (uploaded_files, invalid_files, existing_files, status.HTTP_403_FORBIDDEN)

        if verbose:
            print("Validating recording dates for deployment_object...")
        file_valid = deployment_object.check_dates(recording_dt)
        deployment_objects = [deployment_object]

    elif device_object:
        if verbose:
            print("Determining deployments from device_object and recording dates...")
        deployment_objects = [device_object.deployment_from_date(
            x) for x in recording_dt]
        file_valid = [x is not None for x in deployment_objects]
        deployment_objects = [
            x for x in deployment_objects if x is not None]

    if verbose:
        print("Filtering invalid files based on deployment and recording dates...")
    if deployment_object:
        invalid_files += [{x.name:
                           {"message": f"Recording date time {z} does not exist in {deployment_object}",
                            "status": 400}} for x,
                          y, z in zip(files, file_valid, recording_dt) if not y]
    else:
        invalid_files += [{x.name:
                           {"message": f"no suitable deployment of {device_object} found for recording date time {z}",
                            "status": 400}} for x,
                          y, z in zip(files, file_valid, recording_dt) if not y]

    files = [x for x, y in zip(files, file_valid) if y]

    if len(files) == 0:
        if verbose:
            print("No valid files remain after filtering.")
        return (uploaded_files, invalid_files, existing_files, status.HTTP_400_BAD_REQUEST)

    if len(recording_dt) > 1:
        recording_dt = [x for x, y in zip(
            recording_dt, file_valid) if y]
    if len(extra_data) > 1:
        extra_data = [x for x, y in zip(extra_data, file_valid) if y]
    if data_types is not None:
        if len(data_types) > 1:
            data_types = [x for x, y in zip(
                data_types, file_valid) if y]

    project_task_pks = []
    all_new_objects = []
    all_handler_tasks = []

    for i in range(len(files)):
        file = files[i]
        filename = file.name
        if len(deployment_objects) > 1:
            file_deployment = deployment_objects[i]
        else:
            file_deployment = deployment_objects[0]

        if verbose:
            print(
                f"Processing file: {filename} for deployment: {file_deployment.deployment_device_ID}")

        if request_user:
            if not request_user.has_perm('data_models.change_deployment', file_deployment):
                if verbose:
                    print(
                        f"User does not have permission to attach file {filename} to {file_deployment.deployment_device_ID}.")
                invalid_files.append(
                    {filename: {"message": f"Not allowed to attach files to {file_deployment.deployment_device_ID}", "status": 403}})
                continue

        if len(recording_dt) > 1:
            file_recording_dt = recording_dt[i]
        else:
            file_recording_dt = recording_dt[0]

        if handler_tasks is not None:
            file_handler_task = handler_tasks[i]
        else:
            file_handler_task = None

        if verbose:
            print(f"Localizing recording date time for file: {filename}...")
        file_recording_dt = check_dt(
            file_recording_dt, file_deployment.time_zone)

        if len(extra_data) > 1:
            file_extra_data = extra_data[i]
        else:
            file_extra_data = extra_data[0]

        if data_types is None:
            file_data_type = file_deployment.device_type
        else:
            if len(data_types) > 1:
                file_data_type, created = DataType.objects.get_or_create(
                    name=data_types[i])
            else:
                file_data_type, created = DataType.objects.get_or_create(
                    name=data_types[0])

        if verbose:
            print(f"Setting local path for file: {filename}...")
        file_local_path = os.path.join(
            settings.FILE_STORAGE_ROOT)

        if not multipart or (multipart and multipart_obj is None):

            if verbose:
                print(f"Setting path for file: {filename}...")

            file_path = os.path.join(file_data_type.name,
                                     file_deployment.deployment_device_ID, str(upload_dt.date()))

            file_extension = os.path.splitext(filename)[1]
            new_file_name = get_new_name(file_deployment,
                                         file_recording_dt,
                                         file_local_path,
                                         file_path
                                         )

            file_size = file.size

            file_fullpath = os.path.join(
                file_local_path, file_path, f"{new_file_name}{file_extension}")

            if verbose:
                print(f"Creating database object for: {filename}...")

            if multipart:
                file_extra_data["multipart_complete"] = False

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
            try:
                new_datafile_obj.full_clean()
            except ValidationError as e:
                if verbose:
                    print(
                        f"Error creating database objects for: {filename}...")
                invalid_files.append(
                    {filename: {"message": f"Error creating database records {repr(e)}", "status": 400}})
                continue
            except Exception as e:
                invalid_files.append(
                    {filename: {"message": repr(e), "status": 400}})
                continue

        else:
            file_fullpath = multipart_obj.full_path()

        try:
            if verbose:
                print(f"Saving file to path: {file_fullpath}...")
            handle_uploaded_file(file, file_fullpath, multipart, verbose)
        except Exception as e:
            if verbose:
                print(
                    f"Error handling uploaded file for: {filename} - {repr(e)}")
            invalid_files.append(
                {filename: {"message": repr(e), "status": 400}})
            if multipart:
                # This is a complete failure when multipart
                return (uploaded_files, invalid_files, existing_files, status.HTTP_400_BAD_REQUEST)

            continue

        if not multipart or (multipart and multipart_obj is None):
            if verbose:
                print(f"Setting file URL for: {filename}...")
            new_datafile_obj.set_file_url()
            all_new_objects.append(new_datafile_obj)

        if not multipart or (multipart and multipart_checksum is not None):
            append_tasks = True

            if multipart:
                # do md5 check
                if verbose:
                    print(
                        f"Performing MD5 checksum validation for multipart file: {multipart_obj.original_name}...")
                server_checksum = get_md5(multipart_obj.full_path())
                if verbose:
                    print(
                        f"Server checksum: {server_checksum}, Client checksum: {multipart_checksum}")
                if not multipart_checksum == server_checksum:
                    if verbose:
                        print(
                            f"Checksum mismatch for multipart file: {multipart_obj.original_name}")
                    invalid_files += [{multipart_obj.original_name: {
                        "message": "Multipart file upload checksum mismatch", "status": 400}}]
                    return (uploaded_files, invalid_files, existing_files, status.HTTP_400_BAD_REQUEST)
                else:
                    if verbose:
                        print(
                            f"Checksum validation passed for multipart file: {multipart_obj.original_name}")
                    multipart_extra_data = multipart_obj.extra_data
                    multipart_extra_data['md5_checksum'] = server_checksum
                    multipart_extra_data.pop("multipart_complete")
                    multipart_obj.extra_data = multipart_extra_data
                    multipart_obj.save()

        else:
            append_tasks = False

        if append_tasks:
            if verbose:
                print(f"Fetching deployment tasks for file: {filename}...")
            file_deployment_tasks = list(file_deployment.project.all().values_list(
                'automated_tasks__pk', flat=True))
            file_deployment_tasks = [
                x for x in file_deployment_tasks if x is not None]
            if verbose:
                print(
                    f"Deployment tasks for file {filename}: {file_deployment_tasks}")
            all_handler_tasks.append(file_handler_task)
            if verbose:
                print(f"Handler task for file {filename}: {file_handler_task}")
            project_task_pks.append(file_deployment_tasks)

    final_status = status.HTTP_200_OK

    if len(all_new_objects) > 0 or multipart:
        if len(all_new_objects) > 0:
            if verbose:
                print(
                    f"Bulk creating {len(all_new_objects)} new DataFile objects...")
            uploaded_files = DataFile.objects.bulk_create(all_new_objects)
            uploaded_files_pks = [x.pk for x in uploaded_files]
            if verbose:
                print(
                    f"Created DataFile objects with primary keys: {uploaded_files_pks}")
            final_status = status.HTTP_201_CREATED

        elif multipart:
            if verbose:
                print(
                    f"Using existing multipart object with primary key: {multipart_obj.pk}")
            uploaded_files = [multipart_obj]
            uploaded_files_pks = [multipart_obj.pk]
            if multipart_checksum is not None:
                final_status = status.HTTP_200_OK
            else:
                final_status = status.HTTP_100_CONTINUE

        all_tasks = []

        # For unique tasks, fire off jobs to perform them
        unique_tasks = list(
            set([x for x in all_handler_tasks if x is not None]))

        if len(unique_tasks) > 0:
            for task_name in unique_tasks:
                # get filenames for this task
                task_file_pks = [x for x,
                                 y in zip(uploaded_files_pks, handler_tasks) if y == task_name]
                if len(task_file_pks) > 0:
                    new_task = app.signature(
                        task_name, [task_file_pks], immutable=True)
                    all_tasks.append(new_task)

        # For unique tasks, fire off jobs to perform them
        flat_project_task_pks = [
            x for internal_list in project_task_pks for x in internal_list]

        unique_project_task_pks = list(set(flat_project_task_pks))
        if len(unique_project_task_pks) > 0:
            for project_task_pk in unique_project_task_pks:
                # get filenames for this task
                task_file_pks = [x for x,
                                 y in zip(uploaded_files_pks, project_task_pks) if project_task_pk in y]
                if len(task_file_pks) > 0:
                    # get signature from the db object
                    task_obj = ProjectJob.objects.get(pk=project_task_pk)
                    new_task = task_obj.get_job_signature(task_file_pks)
                    all_tasks.append(new_task)

        if len(all_tasks) > 0:
            task_chain = chain(all_tasks)
            task_chain.apply_async()

    else:
        if verbose:
            print("Determining final status based on invalid files...")
        final_status = status.HTTP_400_BAD_REQUEST
        if all([[y[x].get('status') == 403 for x in y.keys()][0] for y in invalid_files]):
            if verbose:
                print(
                    "All invalid files have a status of 403. Setting final status to HTTP_403_FORBIDDEN.")
            final_status = status.HTTP_403_FORBIDDEN
    return (uploaded_files, invalid_files, existing_files, final_status)


def handle_uploaded_file(file, filepath, multipart=False, verbose=False):
    os.makedirs(os.path.split(filepath)[0], exist_ok=True)
    if multipart and os.path.exists(filepath):
        if verbose:
            print(f"Appending to {filepath}")
        with open(filepath, 'ab+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
    else:
        if verbose:
            print(f"Writing to {filepath}")
        with open(filepath, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)


def clear_uploaded_file(filepath):
    try:
        os.remove(filepath)
    except OSError:
        pass


def get_new_name(deployment, recording_dt, file_local_path, file_path, file_n=None):
    if file_n is None:
        file_n = get_n_files(os.path.join(file_local_path, file_path)) + 1
    newname = f"{deployment.deployment_device_ID}_{dt.strftime(recording_dt, '%Y-%m-%d_%H-%M-%S')}_({file_n})"
    return newname


def get_n_files(dir_path):
    if os.path.exists(dir_path):
        all_files = os.listdir(dir_path)
        # only with extension
        all_files = [x for x in all_files if '.' in x]
        n_files = len(all_files)
    else:
        n_files = 0
    return n_files


def group_files_by_size(file_objs,
                        max_size=settings.MAX_ARCHIVE_SIZE_GB):

    curr_key = 0
    curr_total = 0
    file_info = []

    file_objs = file_objs.order_by('recording_dt')

    file_values = file_objs.values('pk', 'file_size')
    for file_value in file_values:
        file_size = convert_unit(file_value['file_size'], "GB")

        if (curr_total+file_size) > max_size:
            # If the new file would push over the max size, start a new split
            curr_total = file_size
            curr_key += 1
        else:
            curr_total += file_size

        file_info.append(
            {"pk": file_value['pk'], "file_size": file_size, "key": curr_key})

    groups = []

    for k, g in itertools.groupby(file_info, lambda x: x.get("key")):
        files = list(g)

        total_size_gb = sum([x.get('file_size') for x in files])
        file_pks = [x.get('pk') for x in files]
        # Store group iterator as a list
        groups.append({"file_pks": file_pks, "total_size_gb": total_size_gb})

    return groups
