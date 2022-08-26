from django.contrib import admin
from . import models
from django.contrib.auth.models import Group, User
from admin_interface.models import Theme

admin.site.site_url = ''
admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.unregister(Theme)


@admin.register(models.BotAPI)
class BotAPIAdmin(admin.ModelAdmin):
    model = models.BotAPI

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.BotSettings)
class BotSettingsAdmin(admin.ModelAdmin):
    model = models.BotSettings

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(models.AdminTelegramID)
