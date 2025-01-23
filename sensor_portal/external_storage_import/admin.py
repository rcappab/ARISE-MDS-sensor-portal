from django.contrib import admin

# Register your models here.
from utils.admin import GenericAdmin, AddOwnerAdmin
from .models import DataStorageInput


@admin.register(DataStorageInput)
class GenericAdmin(AddOwnerAdmin):
    pass
