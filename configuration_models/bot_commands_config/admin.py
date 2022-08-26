from django.contrib import admin
from . import models


class CommandTextAdmin(admin.StackedInline):
    model = models.CommandText
    extra = 0


class CommandMediaAdmin(admin.StackedInline):
    model = models.CommandMedia
    extra = 0


class UserCommandsButtonsAdmin(admin.StackedInline):
    model = models.CommandsButtonsUser
    extra = 0


@admin.register(models.CommandsConfig)
class CommandsConfigAdmin(admin.ModelAdmin):
    model = models.CommandsConfig
    change = True
    inlines = [CommandTextAdmin, CommandMediaAdmin, UserCommandsButtonsAdmin]

