from django.contrib import admin
from utils.admin import AddOwnerAdmin

from .models import DataPackage

# Register your models here.


@admin.register(DataPackage)
class ObservationAdmin(AddOwnerAdmin):
    model = DataPackage
    raw_id_fields = ["data_files"]
