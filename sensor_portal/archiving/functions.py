import itertools
from data_models.models import DataFile, Deployment, Device, Project
from django.db.models import Min, Max
from utils.general import convert_unit
from django.conf import settings
from .models import TarFile
import os
import hashlib
from datetime import datetime
from utils.general import call_with_output
from data_models.serializers import DataFileSerializer, DeploymentSerializer, DeviceSerializer, ProjectSerializer
import json


def check_archive_projects(archive):
    # Get all projects linked to this archive
    all_project_combos = list(archive.linked_projects.all().values_list(
        "deployments__combo_project", flat=True).distinct())

    for project_combo in all_project_combos:

        all_file_objs = DataFile.objects.filter(
            deployment__combo_project=project_combo, tar_file__isnull=True)

        if not all_file_objs.exists():
            continue

        device_types = list(all_file_objs.values_list(
            "deployment__device__type", flat=True).distinct())
        for device_type in device_types:
            # Get datafiles for this project, sensor type
            file_objs = all_file_objs.filter(
                deployment__device__type=device_type)
            if not file_objs.exists():
                continue

            # check files for archiving
            check_files_for_archiving(file_objs)


def check_files_for_archiving(file_objs):
    total_file_size = file_objs.file_size("GB")
    if total_file_size > settings.MIN_ARCHIVE_SIZE_GB:
        # Assign these files to a dummy TAR
        in_progress_tar = TarFile.objects.get_or_create(
            "in_progress", uploading=True)
        file_objs.update(tar_file=in_progress_tar)

        file_pks = list(file_objs.values_list('pk', flat=True))
        create_tar_files_task(file_pks)  # will be an async task


def create_tar_files_task(file_pks, archive_pk):
    file_objs = DataFile.objects.filter(pks__in=file_pks)
    file_splits_ok = get_tar_splits(file_objs)

    for idx, file_split in enumerate(file_splits_ok):
        file_split_pks = file_split['file_pks']
        file_split_objs = DataFile.objects.filter(pk__in=file_split_pks)
        create_tar_file(file_split_objs, idx)


def get_tar_splits(file_objs):
    file_splits = get_splits(file_objs)

    too_small_split_pks = [
        x for y in file_splits if y["total_size_gb"] < settings.MIN_ARCHIVE_SIZE_GB for x in y['file_pks']]

    # Remove files whose TAR would not be large enough from the in progress tar
    too_small_file_objs = DataFile.objects.filter(pks__in=too_small_split_pks)
    too_small_file_objs.update(tar_file=None)

    file_splits_ok = [
        x for x in file_splits if x["total_size_gb"] >= settings.MIN_ARCHIVE_SIZE_GB]
    return file_splits_ok


def get_tar_name(file_objs, suffix=0):
    min_date = file_objs.aggregate(min_date=Min("recording_dt"))["min_date"]
    min_date_str = min_date.strftime("%Y%m%d")
    max_date = file_objs.aggregate(max_date=Max("recording_dt"))["max_date"]
    max_date_str = max_date.strftime("%Y%m%d")
    combo_project = file_objs.values_list(
        "deployment__combo_project", flat=True).first().replace("-", "").replace(" ", "-")
    device_type = file_objs.values_list(
        "deployment__device__type__name", flat=True).first().replace(" ", "")

    creation_dt = datetime.now().strftime("%Y%m%d_%H%M%S")

    tar_name = ("_").join([combo_project, device_type,
                           min_date_str, max_date_str, creation_dt, str(suffix)])

    return tar_name


def create_tar_file(file_objs, name_suffix=0):

    # get TAR name
    tar_name = get_tar_name(file_objs, name_suffix)
    tar_name_format = tar_name+".tar.gz"
    tar_path = os.path.join(settings.FILE_STORAGE_ROOT,
                            "archiving", datetime.now().strftime("%Y%m%d"))
    os.makedirs(tar_path, exist_ok=True)
    full_tar_path = os.path.join(tar_path, tar_name_format)
    # get list of file paths
    relative_paths = file_objs.relative_paths()

    metadata_dir_path = os.path.join(tar_path, tar_name)
    relative_metadata_dir_path = os.path.relpath(
        metadata_dir_path, settings.FILE_STORAGE_ROOT)

    # Generate bagit metadata
    all_metadata_paths = bag_info_from_files(file_objs, metadata_dir_path)

    # Generate metadata file

    metadata_json_path = metadata_json_from_files(file_objs, metadata_dir_path)

    all_metadata_paths.append(metadata_json_path)

    relative_metadata_paths = [os.path.relpath(
        x, settings.FILE_STORAGE_ROOT) for x in all_metadata_paths]

    # TAR files
    # Use transform command to generate data dir inside the TAR, move metadata files to root

    tar_command = ["tar", "zcvf", full_tar_path,
                   "--transform", f"s,^,data/,;s,data/{relative_metadata_dir_path}/,,",] + relative_paths + relative_metadata_paths
    success, output = call_with_output(tar_command, settings.FILE_STORAGE_ROOT)

    # regardless of status, we remove the metadata files
    [os.remove(x) for x in all_metadata_paths]
    os.removedirs(metadata_dir_path)

    if not success:
        # Free data file objects
        file_objs.update(tar_file=None)
        print("Error creating TAR")
        print(output)
        return False, tar_name, None

    return True, tar_name, full_tar_path


def metadata_json_from_files(file_objs, output_path):
    metadata_dict = create_metadata_dict(file_objs)
    os.makedirs(output_path, exist_ok=True)
    metadata_json_path = os.path.join(output_path, "metadata.json")

    # json dump file
    with open(metadata_json_path, "w") as f:
        f.write(json.dumps(metadata_dict, indent=2))

    return metadata_json_path


def create_metadata_dict(file_objs):
    deployment_objs = Deployment.objects.filter(files__in=file_objs).distinct()
    project_objs = Project.objects.filter(
        deployments__in=deployment_objs).distinct()
    device_objs = Device.objects.filter(
        deployments__in=deployment_objs).distinct()

    file_dict = DataFileSerializer(file_objs, many=True).data
    deployment_dict = DeploymentSerializer(deployment_objs, many=True).data
    project_dict = ProjectSerializer(project_objs, many=True).data
    device_dict = DeviceSerializer(device_objs, many=True).data

    all_dict = {"projects": project_dict, "devices": device_dict,
                "deployments": deployment_dict, "data_files": file_dict}

    return all_dict


def get_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def bag_info_from_files(file_objs, output_path):
    """
    This should generate neccesary files for a bagit object.
    The bagit python implementation requires files to be moved.
    With this script, these text files can be generated an appended straight to a TAR.

    Args:
        file_objs (DataFile): queryset of DataFile objects
        output_folder (str): output folder for generated files
    """
    os.makedirs(output_path, exist_ok=True)

    # bag.txt
    bagit_txt_lines = ["BagIt-Version: 0.97\n",
                       "Tag-File-Character-Encoding: UTF-8\n"]

    bag_path = os.path.join(output_path, "bagit.txt")
    # export file
    with open(bag_path, "w") as f:
        f.writelines(bagit_txt_lines)

    # manifest-md5.txt

    all_full_paths = file_objs.full_paths()
    all_relative_paths = file_objs.relative_paths()

    manifest_lines = [f"{get_md5(x)}  {os.path.join('data',y)}\n" for x, y in zip(
        all_full_paths, all_relative_paths)]

    manifest_path = os.path.join(output_path, "manifest-md5.txt")
    with open(manifest_path, "w") as f:
        f.writelines(manifest_lines)

    # tagmanifest-md5.txt
    # run checksums on previously exported bag txt files

    all_paths = [bag_path, manifest_path]
    tag_manifest_lines = [
        f"{get_md5(x)}  {os.path.split(x)[1]}\n" for x in all_paths]

    tag_manifest_path = os.path.join(output_path, "tagmanifest-md5.txt")

    with open(tag_manifest_path, "w") as f:
        f.writelines(tag_manifest_lines)

    all_paths.append(tag_manifest_path)

    # return paths to these files
    return all_paths


def get_splits(file_objs,
               min_size=settings.MIN_ARCHIVE_SIZE_GB,
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
