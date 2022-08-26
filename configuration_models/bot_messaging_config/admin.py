from django.contrib import admin
from . import models
 

class MessagingTextAdmin(admin.StackedInline): 
    model = models.MessagingText
    extra = 1


class MessagingMediaAdmin(admin.StackedInline):
    model = models.MessagingMedia
    extra = 0


class UserMessagingButtonsAdmin(admin.StackedInline):
    model = models.MessagingButtonsUser
    extra = 0


@admin.register(models.MessagingConfig)
class MessagingConfigAdmin(admin.ModelAdmin):
    model = models.MessagingConfig
    change = True
    inlines = [MessagingTextAdmin, MessagingMediaAdmin, UserMessagingButtonsAdmin]
