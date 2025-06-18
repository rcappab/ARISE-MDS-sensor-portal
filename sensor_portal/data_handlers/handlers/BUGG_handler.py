import io
import os
from datetime import datetime
from typing import Any, List, Tuple

import dateutil.parser
import pandas as pd
import soundfile as sf
from celery import shared_task
from data_handlers.functions import (check_exif_keys, get_image_recording_dt,
                                     open_exif)
from data_handlers.handlers.default_image_handler import DataTypeHandler
from django.core.files import File

from sensor_portal.celery import app


class BUGGHandler(DataTypeHandler):
    data_types = ["audio"]
    device_models = ["BUGG", "BUGGv3"]
    safe_formats = [".mp3"]
    full_name = "BUGG"
    description = """Data handler for BUGG"""
    validity_description = \
        """<ul>

    </ul>
    """.replace("\n", "<br>")
    handling_description = \
        """<ul>

    </ul>
    """.replace("\n", "<br>")

    def handle_file(self, file, recording_dt: datetime = None, extra_data: dict = None, data_type: str = None) -> Tuple[datetime, dict, str]:
        recording_dt, extra_data, data_type, task = super().handle_file(
            file, recording_dt, extra_data, data_type)

        split_filename = os.path.splitext(file.name)

        file_filename = split_filename[0]

        recording_dt = dateutil.parser.parse(
            file_filename.replace("_", ":"), yearfirst=True)

        with sf.SoundFile(file.file, 'rb') as f:

            extra_data.update({
                "sample_rate": f._info.samplerate,
                "duration": float(f._info.frames/f._info.samplerate)
            })

        return recording_dt, extra_data, data_type, task

    def get_post_download_task(self, file_extension: str, first_time: bool = True):
        task = None

        return task
