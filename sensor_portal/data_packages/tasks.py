from datetime import datetime
from uuid import uuid4

from archiving.tasks import get_files_from_archive_task
from celery import shared_task
from data_models.file_handling_functions import group_files_by_size
from data_models.models import DataFile
from data_models.permissions import perms
from django.conf import settings
from user_management.models import User

from .models import DataPackage


@shared_task(name="create_data_package")
def start_make_data_package_task(file_pks, user_pk, metadata_type=0, include_files=True):

    print(file_pks, user_pk)

    file_objs = DataFile.objects.filter(pk__in=file_pks)
    user = User.objects.get(pk=user_pk)

    file_objs = perms['data_models.view_datafile'].filter(user, file_objs)

    min_date = file_objs.min_date()
    min_date_str = min_date.strftime("%Y%m%d")
    max_date = file_objs.max_date()
    max_date_str = max_date.strftime("%Y%m%d")
    creation_dt = datetime.now().strftime("%Y%m%d_%H%M%S")

    all_package_pks = []

    # if files, Split file objs by size, create all bundles
    if include_files:
        file_splits = group_files_by_size(file_objs)

        for suffix, group in enumerate(file_splits):
            bundle_file_objs = file_objs.filter(pk__in=group.get('file_pks'))
            uuid = str(uuid4())

            bundle_name = ("_").join([uuid, user.username,
                                      min_date_str, max_date_str, creation_dt, str(suffix)])
            # Create bundle object
            new_file_bundle = DataPackage.objects.create(
                name=bundle_name, owner=user, metadata_type=metadata_type)

            new_file_bundle.data_files.set(bundle_file_objs)
            all_package_pks.append(new_file_bundle.pk)

        archived_files = file_objs.filter(local_storage=False, archived=True)
        if archived_files.exists():
            bundle_objs = DataPackage.objects.filter(pk__in=all_package_pks)
            bundle_objs.update(status=1)
            archive_callback = make_data_package_task.si(all_package_pks).on_error(
                fail_data_package_task.si(all_package_pks))
            get_files_from_archive_task(file_pks, archive_callback)
            return
        else:
            make_data_package_task(all_package_pks)
            return

    else:
        uuid = str(uuid4())
        bundle_name = ("_").join([uuid, user.username,
                                  min_date_str, max_date_str, creation_dt, str(suffix)])
        new_file_bundle = DataPackage.objects.create(
            name=bundle_name, data_files=file_objs, owner=user, metadata_type=metadata_type, include_files=False)
        all_package_pks.append(new_file_bundle.pk)
        # go straight to finish bundle job
        make_data_package_task(all_package_pks)
        return


@shared_task
def make_data_package_task(all_package_pks):
    bundle_objs = DataPackage.objects.filter(pk__in=all_package_pks)
    bundle_objs.update(status=2)
    for bundle_obj in bundle_objs:
        bundle_obj.make_zip()


@shared_task
def fail_data_package_task(all_package_pks):
    bundle_objs = DataPackage.objects.filter(pk__in=all_package_pks)
    bundle_objs.update(status=4)
