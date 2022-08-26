from django.contrib import admin
from . import models
import nested_admin


class StepMessagingTextAdmin(nested_admin.NestedStackedInline):
    model = models.StepMessagingText
    extra = 1

class StepMessagingMediaAdmin(nested_admin.NestedStackedInline):
    model = models.StepMessagingMedia
    extra = 0

class StepMessagingButtonsUserAdmin(nested_admin.NestedStackedInline):
    model = models.StepMessagingButtonsUser
    extra = 0

class StepMessagingStepAdmin(nested_admin.NestedStackedInline):
    model = models.StepMessagingStep
    extra = 1
    inlines = [StepMessagingTextAdmin, StepMessagingMediaAdmin, StepMessagingButtonsUserAdmin]



class LastMessageTextAdmin(nested_admin.NestedStackedInline):
    model = models.LastMessageText
    extra = 1

class LastMessageMediaAdmin(nested_admin.NestedStackedInline):
    model = models.LastMessageMedia
    extra = 1


class LastMessageButtonsUserAdmin(nested_admin.NestedStackedInline):
    model = models.LastMessageButtonsUser
    extra = 1

class LastMessageConfigAdmin(nested_admin.NestedStackedInline):
    model = models.LastMessageConfig
    inlines = [LastMessageTextAdmin, LastMessageMediaAdmin, LastMessageButtonsUserAdmin]
    extra = 1


@admin.register(models.StepMessagingConfig)
class StepMessagingConfigAdmin(nested_admin.NestedModelAdmin):
    model = models.StepMessagingConfig
    inlines = [LastMessageConfigAdmin, StepMessagingStepAdmin]

