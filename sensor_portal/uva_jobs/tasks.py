import os

from archiving.models import Archive, TarFile
from celery import shared_task
from data_models.models import DataFile
from django.conf import settings
from django.db.models import F, Q, Value
from django.db.models.functions import Concat
from observation_editor.models import Observation
from user_management.models import User

from sensor_portal.celery import app


@app.task()
def fix_file_storage():
    print("Starting fix_file_storage task...")
    file_objs = DataFile.objects.filter(local_storage=True).exclude(
        local_path=settings.FILE_STORAGE_ROOT)

    batch_size = 2000
    total_obs = file_objs.count()
    print(f"Total files to process: {total_obs}")
    for start in range(0, total_obs, batch_size):
        print(
            f"Processing batch {start // batch_size + 1} of {((total_obs - 1) // batch_size) + 1}")
        objs_to_update = []
        batch = file_objs[start:start + batch_size]
        for file_obj in batch.iterator():
            print(f"Updating file ID {file_obj.id}")
            first_part = os.path.split(file_obj.local_path)[1]
            file_obj.local_path = settings.FILE_STORAGE_ROOT
            file_obj.path = os.path.join(first_part, file_obj.path)
            file_obj.set_file_url()
            objs_to_update.append(file_obj)

        DataFile.objects.bulk_update(
            objs_to_update, ["local_path", "path", "file_url"], 500)
    print("Completed fix_file_storage task.")


@app.task()
def fix_tar_paths():
    old_path = "/nfs/archive04/uvaarise"
    surf_archive = Archive.objects.get(name="UVAARISE SURF data archive")
    all_tars = TarFile.objects.filter(path__contains=old_path)
    surf_archive_path = surf_archive.root_folder

    objs_to_update = []
    for tar_obj in all_tars:
        tar_obj.path = tar_obj.path.replace(old_path, surf_archive_path)
        tar_obj.archive = surf_archive
        objs_to_update.append(tar_obj)

    TarFile.objects.bulk_update(objs_to_update, ["path", "archive"])


@app.task()
def fix_obs():

    users = User.objects.all()
    users = users.annotate(full_name=Concat(
        F("first_name"), Value(" "), F("last_name")))
    validation_through_table = Observation.validation_of.through

    obs_to_modify = Observation.objects.filter(Q(extra_data__confidence__isnull=False) |
                                               Q(extra_data__Confidence__isnull=False) |
                                               Q(extra_data__accuracy__isnull=False) |
                                               Q(extra_data__bbox__isnull=False) |
                                               Q(extra_data__classifiedBy__isnull=False) |
                                               Q(extra_data__confirmationOf__isnull=False) |
                                               Q(extra_data__probability__isnull=False)
                                               )
    batch_size = 2000
    total_obs = obs_to_modify.count()
    for start in range(0, total_obs, batch_size):
        print(
            f"Processing batch {start // batch_size + 1} of {((total_obs - 1) // batch_size) + 1}")

        objs_to_update = []
        through_rows_to_add = []
        batch = obs_to_modify[start:start + batch_size]
        for obs in batch.iterator():
            extra_data = obs.extra_data
            change = False
            new_through = False

            if (confidence := extra_data.get("confidence")) is not None or \
                (confidence := extra_data.get("Confidence")) is not None or \
                (confidence := extra_data.get("accuracy")) is not None or \
                    (confidence := extra_data.get("probability")) is not None:
                print(f"Updating confidence for observation ID {obs.id}")
                obs.confidence = confidence
                [extra_data.pop(x) for x in [y for y in [
                    "probability", "confidence", "Confidence", "accuracy"] if y in extra_data.keys()]]
                change = True

            if (bbox := extra_data.get("bbox")) is not None:
                print(f"Updating bounding box for observation ID {obs.id}")
                obs.bounding_box = bbox
                extra_data.pop("bbox")
                change = True

            if (validation := extra_data.get("confirmationOf")) is not None:
                print(f"Updating validation_of for observation ID {obs.id}")
                try:
                    other_obs = Observation.objects.all().get(pk=validation)
                    new_validation = validation_through_table(
                        from_observation_id=obs.pk, to_observation_id=other_obs.pk)
                    through_rows_to_add.append(new_validation)
                    extra_data.pop("confirmationOf")
                    change = True
                    new_through = True
                except Exception as e:
                    print(e)
                    pass

            if (annotated_by := extra_data.get("classifiedBy")) is not None:
                print(f"Updating owner for observation ID {obs.id}")
                try:
                    user_matches = users.filter(full_name=annotated_by)
                    if user_matches.exists():
                        obs.owner = user_matches.first()
                        extra_data.pop("classifiedBy")
                        change = True
                except Exception as e:
                    print(e)
                    pass

            if change:
                obs.extra_data = extra_data
                objs_to_update.append(obs)

        validation_through_table.objects.bulk_create(
            through_rows_to_add, 500)

        Observation.objects.bulk_update(
            objs_to_update, ["extra_data", "owner", "bounding_box", "confidence"], 500)
