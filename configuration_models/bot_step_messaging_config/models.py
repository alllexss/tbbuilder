from django.db import models
from os.path import basename
import configuration_models.bot_settings_config.models as settings_model


# Step Messaging models
class StepMessagingConfig(models.Model):
    step_messaging_title = models.CharField(verbose_name="Step messaging title. For example: 'Brief'", max_length=120, blank=False)
    start_message = models.CharField(verbose_name="After which message or command of User, Bot should start step messaging?", max_length=120, unique=True)
    send_to_admin = models.BooleanField(verbose_name="Send user replies to admin accounts?", default=True)

    class Meta:
        verbose_name = "Step Messaging configuration"
        verbose_name_plural = "Step Messaging configurations"

    def __str__(self):
        return f"Edit configuration for \"{self.step_messaging_title}\""

    def save(self, *args, **kwargs):
        self.start_message = self.start_message.replace(
            "/", "") if self.start_message[0] == "/" else self.start_message
        super().save(*args, **kwargs)
        settings_model.bot_config_generator.generate_config()


class StepMessagingStep(models.Model):
    step_messaging_config = models.ForeignKey(
        StepMessagingConfig, on_delete=models.CASCADE)
    step_name = models.CharField(
        verbose_name="Step name", unique=True, max_length=120, blank=False)
    send_first = models.CharField(verbose_name="Send first", choices=(
        ("text", "Text Message"), ("media", "Media Message")), max_length=20, default="text")

    class Meta:
        verbose_name = "Step"
        verbose_name_plural = "Steps"

    def __str__(self):
        return f"{self.step_name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        settings_model.bot_config_generator.generate_config()


class StepMessagingText(models.Model):
    step = models.ForeignKey(StepMessagingStep, on_delete=models.CASCADE)
    text = models.TextField(verbose_name="Enter your text for Bot message")

    class Meta:
        verbose_name = "Bot's text message for replying to User"
        verbose_name_plural = "Bot's text messages for replying to User"

    def __str__(self):
        return "Text or HTML format"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        settings_model.bot_config_generator.generate_config()


class StepMessagingMedia(models.Model):
    step = models.ForeignKey(StepMessagingStep, on_delete=models.CASCADE)
    media_file = models.FileField(
        verbose_name="Add your media file to Bot message", upload_to="bot-media-files")
    caption = models.TextField(verbose_name="Caption", blank=True)

    class Meta:
        verbose_name = "Media file for replying to User"
        verbose_name_plural = "Media files for replying to User"

    def __str__(self):
        return basename(self.media_file.name)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        settings_model.bot_config_generator.generate_config()


class StepMessagingButtonsUser(models.Model):
    step = models.ForeignKey(StepMessagingStep, on_delete=models.CASCADE)
    button_1 = models.CharField(max_length=21, verbose_name="Button №1 text")
    type_button1 = models.CharField(verbose_name="Button №1 type", choices=(("text", "Text button"), (
        "location", "Ask location"), ("phone", "Ask phone number")), max_length=20, default="text")
    button_2 = models.CharField(
        max_length=21, verbose_name="Button №2 text", blank=True)
    type_button2 = models.CharField(verbose_name="Button №2 type", choices=(("text", "Text button"), (
        "location", "Ask location"), ("phone", "Ask phone number")), max_length=20, default="text", blank=True)
    button_3 = models.CharField(
        max_length=21, verbose_name="Button №3 text", blank=True)
    type_button3 = models.CharField(verbose_name="Button №3 type", choices=(("text", "Text button"), (
        "location", "Ask location"), ("phone", "Ask phone number")), max_length=20, default="text", blank=True)

    class Meta:
        verbose_name = "User button for replying to Bot"
        verbose_name_plural = "User button for replying to Bot"

    def __str__(self):
        return "User buttons"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        settings_model.bot_config_generator.generate_config()


# Last Messages models
class LastMessageConfig(models.Model):
    config = models.ForeignKey(StepMessagingConfig, on_delete=models.CASCADE)
    send_first = models.CharField(verbose_name="Send first", choices=(
        ("text", "Text Message"), ("media", "Media Message")), max_length=20, default="text")

    class Meta:
        verbose_name = "Last Message"
        verbose_name_plural = "Last Messages"

    def __str__(self):
        return ""

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        settings_model.bot_config_generator.generate_config()


class LastMessageText(models.Model):
    config = models.ForeignKey(LastMessageConfig, on_delete=models.CASCADE)
    text = models.TextField(verbose_name="Enter your text for last message in this step messaging")

    class Meta:
        verbose_name = "Bot's text for last message"
        verbose_name_plural = "Bot's text for last messages"

    def __str__(self):
        return "Text or HTML format"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        settings_model.bot_config_generator.generate_config()


class LastMessageMedia(models.Model):
    config = models.ForeignKey(LastMessageConfig, on_delete=models.CASCADE)
    media_file = models.FileField(
        verbose_name="Add your media file to Bot message", upload_to="bot-media-files")
    caption = models.TextField(verbose_name="Caption", blank=True)

    class Meta:
        verbose_name = "Bot's media for last message"
        verbose_name_plural = "Bot's media for last messages"

    def __str__(self):
        return basename(self.media_file.name)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        settings_model.bot_config_generator.generate_config()


class LastMessageButtonsUser(models.Model):
    config = models.ForeignKey(LastMessageConfig, on_delete=models.CASCADE)
    button_1 = models.CharField(max_length=21, verbose_name="Button №1 text")
    type_button1 = models.CharField(verbose_name="Button №1 type", choices=(("text", "Text button"), (
        "location", "Ask location"), ("phone", "Ask phone number")), max_length=20, default="text")
    button_2 = models.CharField(
        max_length=21, verbose_name="Button №2 text", blank=True)
    type_button2 = models.CharField(verbose_name="Button №2 type", choices=(("text", "Text button"), (
        "location", "Ask location"), ("phone", "Ask phone number")), max_length=20, default="text", blank=True)
    button_3 = models.CharField(
        max_length=21, verbose_name="Button №3 text", blank=True)
    type_button3 = models.CharField(verbose_name="Button №3 type", choices=(("text", "Text button"), (
        "location", "Ask location"), ("phone", "Ask phone number")), max_length=20, default="text", blank=True)

    class Meta:
        verbose_name = "User button for last message from bot"
        verbose_name_plural = "User buttons for last message from bot"

    def __str__(self):
        return "User buttons"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        settings_model.bot_config_generator.generate_config()
