from datetime import datetime as dt
from PIL import ExifTags, Image, TiffImagePlugin


def open_exif(uploaded_file):
    si = uploaded_file.file
    image = Image.open(si)
    image_exif = {ExifTags.TAGS[k]: v for k,
                  v in image.getexif().items() if k in ExifTags.TAGS}

    return image_exif


def check_exif_keys(image_exif, exif_keys, round_val=2):
    new_data = {}

    for exif_key in exif_keys:
        val = image_exif.get(exif_key)
        if val is not None:
            if type(val) is TiffImagePlugin.IFDRational:
                val = float(val)
            if type(val) is float:
                val = round(val, round_val)
            new_data[exif_key] = val

    return new_data


def get_image_recording_dt(image_exif):

    recording_dt = image_exif.get('DateTimeOriginal')
    if recording_dt is None:
        recording_dt = image_exif.get('DateTime')
    if recording_dt is None:
        return None
    return dt.strptime(recording_dt, '%Y:%m:%d %H:%M:%S')
