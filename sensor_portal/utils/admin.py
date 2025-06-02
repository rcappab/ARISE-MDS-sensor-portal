from django.contrib import admin

from .paginators import LargeTablePaginator


class GenericAdmin(admin.ModelAdmin):
    readonly_fields = ['created_on', 'modified_on']
    paginator = LargeTablePaginator
    show_full_result_count = False


class AddOwnerAdmin(GenericAdmin):
    readonly_fields = ['owner']

    def save_model(self, request, obj, form, change):
        if obj.owner is None:
            obj.owner = request.user
        super().save_model(request, obj, form, change)
