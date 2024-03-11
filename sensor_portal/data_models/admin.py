from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(DataType,Site)
class GenericAdmin(admin.ModelAdmin):
     readonly_fields = ['created_on','modified_on']

class AddOwnerAdmin(GenericAdmin):
    def save_model(self, request, obj, form, change):
        if obj.owner is None:
            obj.owner = request.user
        super().save_model(request, obj, form, change)


@admin.register(Device)
class DeviceAdmin(AddOwnerAdmin):
    list_display = ['deviceID', 'type']
    search_fields = ['deviceID']
    list_filter = ['type']


@admin.register(Project)
class ProjectAdmin(AddOwnerAdmin):
    list_display = ['projectID', 'projectName']
    search_fields = ['projectID', 'projectName']



@admin.register(Deployment)
class DeployAdmin(AddOwnerAdmin):
    list_display = ['deployment_deviceID', 'device_type', 'is_active', 'modified_on', 'combo_project']
    search_fields = ['deployment_deviceID']
    list_filter = ['is_active', 'device_type']
    readonly_fields = GenericAdmin.readonly_fields + ['deployment_deviceID', 'combo_project']
    autocomplete_fields = ('device', 'project')


@admin.register(DataFile)
class FileAdmin(GenericAdmin):
    list_display = ['file_name', 'file_type', 'deployment', 'archived', 'localstorage', 'created_on']
    search_fields = ['filename']
    list_filter = ['archived', 'localstorage', 'file_type']
