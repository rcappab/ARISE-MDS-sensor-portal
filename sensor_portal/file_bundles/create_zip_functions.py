import json
import os
from zipfile import ZipFile

from camtrap_dp_export.metadata_functions import create_camtrap_dp_metadata
from data_models.metadata_functions import create_metadata_dict
from django.conf import settings
from django.db.models import F, Value
from django.db.models.functions import Concat
from observation_editor.metadata_functions import \
    create_metadata_dict as create_obs_metadata_dict
from observation_editor.models import Observation


def create_zip(zip_name, file_objs, metadata_type):
    bundle_path = os.path.join(settings.STORAGE, settings.BUNDLE_PATH)
    os.makedirs(bundle_path, exist_ok=True)

    if ".zip" not in zip_name:
        zip_name = f"{zip_name}.zip"

    file_objs = file_objs.full_paths()

    match metadata_type:
        case 0:
            file_objs.annotate(zip_path=Concat(
                Value('data'), Value(os.sep), F('relative_path')))
        case 1:
            file_objs.annotate(
                zip_path=Concat(Value('media'), Value(os.sep), F('relative_path')))
        case _:
            return False, ""

    with ZipFile(os.path.join(bundle_path, zip_name), 'w') as zip_file:
        for file_obj in file_objs:
            zip_file.write(file_obj.full_path, file_obj.new_path)

        match metadata_type:
            case 0:
                metadata_dict = create_metadata_dict(file_objs)
                observation_dict = create_obs_metadata_dict(
                    Observation.objects.filter(data_files__in=file_objs))

                with zip_file.open("metadata.json", "w") as f:
                    f.write(json.dumps(metadata_dict, indent=2).encode("utf-8"))

                with zip_file.open("observations.json", "w") as f:
                    f.write(json.dumps(observation_dict,
                            indent=2).encode("utf-8"))

            case 1:
                file_df, observation_df, deploy_df, event_df, metadata = create_camtrap_dp_metadata(
                    file_objs, "", zip_name)
                with zip_file.open("media.csv", "w") as df:
                    file_df.to_csv(df, index=False)

                with zip_file.open("observations.csv", "w") as df:
                    observation_df.to_csv(df, index=False)

                with zip_file.open("deployments.csv", "w") as df:
                    deploy_df.to_csv(df, index=False)

                with zip_file.open("events.csv", "w") as df:
                    event_df.to_csv(df, index=False)

                with zip_file.open("datapackage.json", "w") as f:
                    f.write(json.dumps(metadata, indent=2).encode("utf-8"))

            case _:
                return False, ""

    return True, bundle_path
