from data_handlers.handlers.default_image_handler import DataTypeHandler
from datetime import datetime
from typing import Tuple
from data_handlers.functions import open_exif, check_exif_keys, get_image_recording_dt
import os
import dateutil.parser


class Snyper4GHandler(DataTypeHandler):
    data_types = ["wildlifecamera", "timelapsecamera"]
    device_models = ["default"]
    safe_formats = [".jpg", ".jpeg", ".txt"]
    full_name = "Wide 4G handler"
    description = """Data handler for wide 4G handler"""
    validity_description = """<ul>
    <li>File format must be in available formats.</li>
    <li>Image naming convention must be in the format []-[Image type (ME, TL, DR)]-[]., e.g '860946060409946-ME-27012025134802-SYPW1128' or '860946060409946-DR-27012025120154-SYPW1120'</li>
    <li>Text file must be in the structure of SOMETHING</li>
    </ul>"""
    handling_description = """<ul>
    <li>Recording datetime is extracted from exif.</li>
    <li><strong>Extra metadata attached:</strong>
    <ul>
    <li> YResolution, XResolutiom, Software: extracted from exif</li>
    <li> 'daily_report': Added if the file is a daily report text file or image. Extracted from filename or format.
    </ul>
    </li>
    </ul>"""

    def handle_file(self, file, recording_dt: datetime = None, extra_data: dict = None, data_type: str = None) -> Tuple[datetime, dict, str]:
        recording_dt, extra_data, data_type = super().handle_file(
            file, recording_dt, extra_data, data_type)

        split_filename = os.path.splitext(file.name)
        file_extension = split_filename[1]

        if file_extension == ".txt":
            report_dict = {}
            # Should extract date time from file
            for line in file:
                line_split = line.split(":", 1)
                line_split[1] = line_split[1].replace("\n", "")

                if line_split[0] not in report_dict.keys():
                    report_dict[line_split[0]] = []

                report_dict[line_split[0]].append(line_split[1])

            dates = [dateutil.parser.parse(x, dayfirst=True)
                     for x in report_dict['Date']]
            recording_dt = min(dates)

            extra_data["daily_report"] = True
        else:
            split_image_filename = split_filename[0].split("-")

            match split_image_filename[1]:
                case "TL":
                    data_type = "timelapsecamera"
                case "DR":
                    data_type = "timelapsecamera"
                    extra_data["daily_report"] = True
                case "ME":
                    data_type = "wildlifecamera"
                case _:
                    data_type = "wildlifecamera"

            image_exif = open_exif(file)
            recording_dt = get_image_recording_dt(image_exif)

            # YResolution XResolution Software
            new_extra_data = check_exif_keys(image_exif, [
                "YResolution", "XResolution", "Software"])

            extra_data.update(new_extra_data)

        return recording_dt, extra_data, data_type
