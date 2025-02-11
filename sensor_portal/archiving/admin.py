from django.contrib import admin
from utils.admin import GenericAdmin, AddOwnerAdmin
from .models import Archive, TarFile
from .forms import ArchiveForm


@admin.register(Archive)
class ArchiveAdmin(AddOwnerAdmin):
    form = ArchiveForm


@admin.register(TarFile)
class TarFileAdmin(GenericAdmin):
    pass
