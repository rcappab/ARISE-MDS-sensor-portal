import os
from datetime import datetime
from typing import Any, List, Tuple

from aerocam_handler.reader import DatReader
from celery import shared_task
from data_handlers.base_data_handler_class import DataTypeHandler


class AeroCamHandler(DataTypeHandler):
    data_types = ["aeroecologycamera"]
    device_models = ["default"]
    safe_formats = [".dat"]
    full_name = "Aeroecology handler"
    description = """Data handler for aeroecology files."""
    validity_description =\
        """
    <ul>
    <li>Must be a swiss bird radar aerocam dat file</li>
    </ul>
    """
    handling_description = \
        """
    <ul>
    <li>dat files are decoded for human viewing</li>
    </li>
    </ul>
    """

    def handle_file(self, file, recording_dt: datetime = None, extra_data: dict = None, data_type: str = None) -> Tuple[datetime, dict, str]:

        recording_dt, extra_data, data_type, task = super().handle_file(
            file, recording_dt, extra_data, data_type)

        if recording_dt is None:
            recording_dt = datetime.now()

        return recording_dt, extra_data, data_type, task

    def get_post_download_task(self, file_extension: str, first_time: bool = True):
        # Always convert the file
        return "aerocam_converter"


@shared_task(name="aerocam_converter")
def aerocam_converter_task(file_pks: List[int]):
    from data_handlers.post_upload_task_handler import post_upload_task_handler
    from data_models.models import DataFile, Deployment

    post_upload_task_handler(file_pks, aerocam_convert)

    deployment_pk = DataFile.objects.filter(pk__in=file_pks).values_list(
        'deployment__pk', flat=True).distinct()
    deployment_objs = Deployment.objects.filter(pk__in=deployment_pk)
    for deployment_obj in deployment_objs:
        deployment_obj.set_thumb_url()

    Deployment.objects.bulk_update(deployment_objs, ["thumb_url"])


def aerocam_convert(data_file) -> Tuple[Any | None, List[str] | None]:
    dat_file_path = data_file.full_path()

    # Create DatReader instance
    dat_handler = DatReader()

    thumb_path = os.path.join(os.path.split(
        dat_file_path)[0], data_file.file_name+"_THUMB.jpg")

    concat_path = os.path.join(os.path.split(
        dat_file_path)[0], data_file.file_name+"_CONCAT.jpg")

    anim_path = os.path.join(os.path.split(
        dat_file_path)[0], data_file.file_name+"_ANIM.gif")

    # Load a file
    with open(dat_file_path, 'rb') as f:
        dat_handler.open_dat_file(f)

    if dat_handler.image_list:
        # Get largest image from sequence to use as a thumbnail
        thumb = max(dat_handler.image_list,
                    key=lambda img: img.size[0] * img.size[1]).copy()
        thumb.thumbnail((100, 100))
        thumb.save(thumb_path)
    else:
        thumb = None

    dat_handler.save_concatenated_image(concat_path)

    dat_handler.save_animation(anim_path)

    data_file.set_thumb_url()
    data_file.linked_files = {
        "Image": {"path": concat_path}, "Animation": {"path": anim_path}}
    data_file.set_linked_files_urls()
    return data_file, ["thumb_url", "linked_files"]
