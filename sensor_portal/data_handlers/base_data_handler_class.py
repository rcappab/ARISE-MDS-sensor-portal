import importlib
import os
from typing import Any, Callable, Tuple
from datetime import datetime
from typing import List, Callable


class DataTypeHandler():
    data_types = ["default"]
    device_models = ["default"]
    safe_formats = [""]
    full_name = "No name provided"
    description = "No description provided"
    validity_description = "No validity description provided"
    handling_description = "No handling description provided"

    def format_check(self, file, device_label=None):
        return os.path.splitext(file.name)[1].lower() in self.safe_formats

    def all_file_format_check(self, files, device_label=None):
        for file in files:
            if self.format_check(file, device_label):
                return True
        return False

    def get_valid_files(self, files, device_label=None):
        return [x for x in files if self.format_check(x, device_label)]

    def handle_file(self,
                    file,
                    recording_dt: datetime = None,
                    extra_data: dict = None,
                    data_type: str = None) -> Tuple[datetime, dict, str, str]:

        if extra_data is None:
            extra_data = {}

        return recording_dt, extra_data, data_type, None


class DataTypeHandlerCollection():

    data_type_handlers = {}

    def __init__(self, root_path="") -> None:
        handler_dir = os.path.join(
            root_path, "data_handlers", "handlers")
        handler_files = [os.path.splitext(x)[0] for x in os.listdir(
            handler_dir) if os.path.splitext(x)[1] == '.py']

        for handler_file in handler_files:
            importlib.import_module(
                f"data_handlers.handlers.{handler_file}")

        all_handlers = DataTypeHandler.__subclasses__()
        for handler in all_handlers:
            for data_type in handler.data_types:
                if not self.data_type_handlers.get(data_type):
                    self.data_type_handlers[data_type] = {}
                for model in handler.device_models:
                    self.data_type_handlers[data_type][model] = handler()

    def set_default_model(self, data_type, device_model):

        if data_type not in self.data_type_handlers.keys():
            return None

        if device_model not in self.data_type_handlers[data_type].keys()\
                or self.data_type_handlers.get(data_type) is None:
            device_model = "default"
        return device_model

    def get_valid_files(self, data_type, device_model, files, device_label=None):

        device_model = self.set_default_model(data_type, device_model)

        if device_model is None:
            return []

        return self.data_type_handlers[data_type][device_model].get_valid_files(files, device_label)

    def check_valid_files(self, data_type, device_model, files, device_label=None):
        device_model = self.set_default_model(data_type, device_model)

        if device_model is None:
            return False

        return self.data_type_handlers[data_type][device_model].all_file_format_check(files, device_label)

    def check_handlers(self, data_type, device_model):

        if self.data_type_handlers.get(data_type) is None:
            return False

        device_model = self.set_default_model(data_type, device_model)

        return self.data_type_handlers[data_type].get(device_model)

    def get_handler(self, data_type, device_model) -> type[DataTypeHandler]:
        device_model = self.set_default_model(data_type, device_model)
        if device_model is None:
            return None
        print(f"Got data handler {data_type} {device_model}")
        return self.data_type_handlers[data_type][device_model]

    def get_file_handler(self, data_type, device_model) -> Callable:

        device_model = self.set_default_model(data_type, device_model)

        if device_model is None:
            return None
        print(f"Got data handler {data_type} {device_model}")
        return self.data_type_handlers[data_type][device_model].handle_file


def post_upload_task_handler(file_pks: List[int],
                             task_function: Callable[[Any], Tuple[Any | None, List[str] | None]]) -> None:
    # Due to the way the data_handler imports work, cannot import the data model to type this more strongly
    """
Wrapper function to handle applying post upload functions on files. Will lock any files being operated on, return them to their initial lock state when done.

Args:
    file_pks (List[int]): list of DataFile primary keys. These will be the files on which task_function is called.
    task_function (Callable[[DataFile], Tuple[DataFile  |  None, List[str]  |  None]]): Function to carry out on each DataFile.

    task_function Should take the DataFile as arguments and return a modified DataFile and a list of the names of the modified fields.
    """
    from data_models.models import DataFile
    # get datafiles
    data_file_objs = DataFile.objects.filter(
        pk__in=file_pks).order_by("created_on")
    # save initial do_not_delete state of files

    do_not_remove_initial = data_file_objs.values_list(
        "do_not_remove", flat=True)

    # lock datafiles
    data_file_objs.update(do_not_remove=True)

    updated_data_objs = []

    # loop through datafiles
    for i, data_file in enumerate(data_file_objs):

        file_do_not_remove = do_not_remove_initial[i]

        updated_data_file, modified_fields = task_function(
            data_file, file_do_not_remove)
        if updated_data_file is not None:
            updated_data_file.do_not_remove = file_do_not_remove
            updated_data_objs.append(updated_data_file)

    if "do_not_remove" not in modified_fields:
        modified_fields.append("do_not_remove")

    # update objects
    DataFile.objects.bulk_update(updated_data_objs, modified_fields)
