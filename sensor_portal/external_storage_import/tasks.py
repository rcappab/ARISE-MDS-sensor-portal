from sensor_portal.celery import app


@app.task()
def check_external_storage_input_task(storage_pk: int):
    from .models import DataStorageInput
    storage = DataStorageInput.objects.get(storage_pk)
    storage.check_input()


@app.task()
def check_external_storage_users_task(storage_pk: int):
    from .models import DataStorageInput
    storage = DataStorageInput.objects.get(storage_pk)
    storage.setup_users()
