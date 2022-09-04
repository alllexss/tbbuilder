from django.db import models
from os.path import basename
import configuration_models.bot_settings_config.models as settings_model


class CommandsConfig(models.Model):
    name = models.CharField(verbose_name="Command ( Without '/' )", max_length=120, unique=True)
    text = models.TextField(verbose_name="Enter your text message for replying", null=True)
    send_first = models.CharField(verbose_name="Send first", choices=(("text", "Text Message"),("media", "Media Message")), max_length=20, default="text")

    class Meta:
        verbose_name = "Command replying configuration"
        verbose_name_plural = "Commands replying configurations"

    def __str__(self):
        return f"/{self.name}"

    def save(self, *args, **kwargs):
        self.name = self.name.replace("/", "")
        super().save(*args, **kwargs)
        settings_model.bot_config_generator.generate_config()


class CommandText(models.Model):
    parent_command = models.ForeignKey(CommandsConfig, on_delete=models.CASCADE)
    text = models.TextField(verbose_name="Enter your additional text for message")

    class Meta:
        verbose_name = "Additional Text Message for Reply"
        verbose_name_plural = "Additional Text Messages for Reply"


    def __str__(self):
        return "Text or HTML format"


class CommandMedia(models.Model):
    parent_command = models.ForeignKey(CommandsConfig, on_delete=models.CASCADE)
    caption = models.TextField(verbose_name="Caption", blank=True)
    media_file = models.FileField(verbose_name="Add your media file for message", upload_to="bot-media-files")

    class Meta:
        verbose_name = "Media Message for Reply"
        verbose_name_plural = "Media Messages for Reply"

    def __str__(self):
        return basename(self.media_file.name)


class CommandsButtonsUser(models.Model):
    parent_command = models.ForeignKey(CommandsConfig, on_delete=models.CASCADE)
    button_1 = models.CharField(max_length=21, verbose_name="Button №1 text")
    type_button1 = models.CharField(verbose_name="Button №1 type", choices=(("text", "Text button"), ("location", "Ask location"),("phone", "Ask phone number")), max_length=20, default="text")
    button_2 = models.CharField(max_length=21, verbose_name="Button №2 text", blank=True)
    type_button2 = models.CharField(verbose_name="Button №2 type", choices=(("text", "Text button"), ("location", "Ask location"),("phone", "Ask phone number")), max_length=20, default="text", blank=True)
    button_3 = models.CharField(max_length=21, verbose_name="Button №3 text", blank=True)
    type_button3 = models.CharField(verbose_name="Button №3 type", choices=(("text", "Text button"), ("location", "Ask location"),("phone", "Ask phone number")), max_length=20, default="text", blank=True)


    class Meta:
        verbose_name = "User button"
        verbose_name_plural = "User buttons"

    def __str__(self):
        return "/" + self.parent_command.name
