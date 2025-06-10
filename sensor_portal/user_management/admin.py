from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from rest_framework.authtoken.admin import TokenAdmin
from rest_framework.authtoken.models import Token, TokenProxy

from .models import DeviceUser, User

TokenAdmin.raw_id_fields = ['user']


class TokenInline(admin.StackedInline):
    model = Token
    # readonly_fields = ["key"]


admin.site.unregister(TokenProxy)


class InlineUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name',
                    'last_name', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'groups')
    search_fields = ('username', 'first_name', 'last_name')

    readonly_fields = ["last_login"]

    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {'fields': ('organisation', 'bio')}),
    )

    inlines = [
        TokenInline,
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(deviceuser__isnull=True)

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            # hide Token in the add view
            if not isinstance(inline, TokenInline) or obj is not None:
                yield inline.get_formset(request, obj), inline

    def save_model(self, request, obj, form, change):
        obj.from_admin_site = True
        super().save_model(request, obj, form, change)

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'first_name', 'last_name', 'username', 'password1', 'password2'),
            },
        ),
    )


admin.site.register(User, InlineUserAdmin)


class DeviceUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'device', 'email')
    list_filter = ()
    search_fields = ('username',)
    exclude = ['first_name', 'last_name',
               'is_staff', 'is_active', 'is_superuser', 'groups', 'date_joined', 'last_login', 'user_permissions',
               'password', 'organisation', 'bio', ]
    readonly_fields = ["username", "device", 'email']

    inlines = [
        TokenInline,
    ]

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            # hide Token in the add view
            if not isinstance(inline, TokenInline) or obj is not None:
                yield inline.get_formset(request, obj), inline

    def save_model(self, request, obj, form, change):
        obj.from_admin_site = True
        super().save_model(request, obj, form, change)


admin.site.register(DeviceUser, DeviceUserAdmin)
