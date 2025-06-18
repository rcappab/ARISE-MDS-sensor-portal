import json
import os

from django.db.models import QuerySet

from .models import DataFile, Deployment, Device, Project
from .serializers import (DataFileSerializer, DeploymentSerializer,
                          DeviceSerializer, ProjectSerializer)


def metadata_json_from_files(file_objs: QuerySet[DataFile], output_path: str):
    """
    Generates a JSON file containing metadata from a collection of data files.
    Args:
        file_objs (QuerySet[DataFile]): A queryset of DataFile objects containing metadata.
        output_path (str): The directory path where the metadata JSON file will be saved.
    Returns:
        str: The file path of the generated metadata JSON file.
    Raises:
        OSError: If there is an issue creating the output directory or writing the file.
    Notes:
        - The function creates a directory at the specified `output_path` if it does not exist.
        - The metadata is serialized into a JSON file named "metadata.json" with an indentation of 2.
    """

    metadata_dict = create_metadata_dict(file_objs)
    os.makedirs(output_path, exist_ok=True)
    metadata_json_path = os.path.join(output_path, "metadata.json")

    # json dump file
    with open(metadata_json_path, "w") as f:
        f.write(json.dumps(metadata_dict, indent=2))

    return metadata_json_path


def create_metadata_dict(file_objs: QuerySet[DataFile]) -> dict:
    """
    Generates a metadata dictionary containing serialized information about projects, devices, deployments,
    and data files associated with the given file objects.
    Args:
        file_objs (QuerySet[DataFile]): A queryset of DataFile objects for which
        metadata needs to be generated.
    Returns:
        dict: A dictionary containing serialized metadata with the following keys:
            - "projects": List of serialized Project objects associated with the deployments.
            - "devices": List of serialized Device objects associated with the deployments.
            - "deployments": List of serialized Deployment objects associated with the file objects.
            - "data_files": List of serialized DataFile objects from the input queryset.
    """

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
