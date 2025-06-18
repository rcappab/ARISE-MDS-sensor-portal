
import os
import random
from datetime import datetime
from typing import Optional, Union

import dateutil.parser
import pytz
from django.conf import settings
from django.utils import timezone as djtimezone
from PIL import Image


def check_dt(
    dt: Optional[Union[datetime, str]],
    device_timezone: Optional[pytz.timezone] = None,
    localise: bool = True
) -> Optional[datetime]:
    """
    Validates and processes a datetime object or string.
    This function ensures that the provided datetime (`dt`) is properly parsed 
    and localized to the specified timezone (`device_timezone`). If no timezone 
    is provided, it defaults to the application's timezone defined in settings. 
    Additionally, it can parse datetime strings into datetime objects.
    Args:
        dt (datetime or str or None): The datetime object or string to validate 
            and process. If None, the function returns None.
        device_timezone (pytz.timezone, optional): The timezone to localize the 
            datetime to. Defaults to the application's timezone.
        localise (bool, optional): Whether to localize the datetime if it is 
            naive (i.e., lacks timezone information). Defaults to True.
    Returns:
        datetime or None: The processed datetime object, localized if applicable, 
        or None if the input `dt` is None.
    """
    # If the input datetime is None, return None immediately.
    if dt is None:
        return dt

    # If no device timezone is provided, use the default timezone from settings.
    if device_timezone is None:
        device_timezone = pytz.timezone(settings.TIME_ZONE)

    # If the input datetime is a string, parse it into a datetime object.
    # The parsing assumes dayfirst=False and yearfirst=True for the format.
    if isinstance(dt, str):
        dt = dateutil.parser.parse(dt, dayfirst=False, yearfirst=True)

    # If the datetime object is naive (lacks timezone info) and localization is enabled,
    # localize it to the specified device timezone.
    if dt.tzinfo is None and localise:
        mytz = device_timezone
        dt = mytz.localize(dt)

    return dt


def create_image(
    image_width: int = 500,
    image_height: int = 500,
    colors: list[tuple[int, int, int]] = [
        (255, 0, 0), (0, 0, 255), (255, 255, 0)]
) -> Image:
    """
    Creates an image with random pixel colors from the specified list of colors.
    Args:
        image_width (int): The width of the image in pixels. Defaults to 500.
        image_height (int): The height of the image in pixels. Defaults to 500.
        colors (list[tuple[int, int, int]]): A list of RGB color tuples to randomly assign to pixels. 
            Defaults to [(255, 0, 0), (0, 0, 255), (255, 255, 0)].
    Returns:
        Image: A PIL Image object with the specified dimensions and randomly colored pixels.
    """

    image = Image.new('RGB', (image_width, image_height))
    for x in range(image.width):
        for y in range(image.height):
            image.putpixel((x, y), random.choice(colors))
    return image
