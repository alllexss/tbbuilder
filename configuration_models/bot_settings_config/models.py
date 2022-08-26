import json
from django.db import models
import configuration_models.bot_commands_config.models as command_model
import configuration_models.bot_messaging_config.models as messaging_model
import configuration_models.bot_step_messaging_config.models as step_messaging_model

bot_config = {
    "API": "",
    "Settings": {},
    "Commands": {},
    "Messaging": {},
    "Step-Messaging": {}
}


def generate_bot_config():
    '''In this function I getting all objects from this models for telegram bot and put it into dictionary'''
    # Getting API 
    bot_config["API"] = BotAPI.objects.first().api

    # Getting settings
    for setting in BotSettings.objects.all():
        bot_config["Settings"]["non_stop"] = setting.non_stop

    # Gettings administrator IDs
    bot_config["Administrator-IDs"] = [int(obj.admin_id) for obj in AdminTelegramID.objects.all()]

    # Getting commands
    for command in command_model.CommandsConfig.objects.all():
        bot_config["Commands"][command.name] = {
            "bot_text": command.text,
            "media_first": True if command.send_first == "media" else False,
            "bot_additional_text": [text.text for text in command_model.CommandText.objects.filter(parent_command__id=command.id)],
            "bot_media": {media.media_file.path: media.caption for media in command_model.CommandMedia.objects.filter(parent_command__id=command.id)},
            "user_buttons": [
                {
                    button.button_1: button.type_button1, 
                    button.button_2: button.type_button2, 
                    button.button_3: button.type_button3
                } for button in command_model.CommandsButtonsUser.objects.filter(parent_command__id=command.id)
            ]
        }

    # Getting messages
    for messaging in messaging_model.MessagingConfig.objects.all():
        bot_config["Messaging"][messaging.message] = {
            "bot_text": messaging.text,
            "media_first": True if messaging.send_first == "media" else False,
            "bot_additional_text": [text.text for text in messaging_model.MessagingText.objects.filter(parent_message__id=messaging.id)],
            "bot_media": {media.media_file.path: media.caption for media in messaging_model.MessagingMedia.objects.filter(parent_message__id=messaging.id)},
            "user_buttons": [
                {
                    button.button_1: button.type_button1, 
                    button.button_2: button.type_button2, 
                    button.button_3: button.type_button3
                } for button in messaging_model.MessagingButtonsUser.objects.filter(parent_message__id=messaging.id)
            ]
        }

    # Getting step messages
    for step_msg_conf in step_messaging_model.StepMessagingConfig.objects.all():
        bot_config["Step-Messaging"][step_msg_conf.start_message] = {}
        for step in step_messaging_model.StepMessagingStep.objects.filter(step_messaging_config__id=step_msg_conf.id):
            bot_config["Step-Messaging"][step_msg_conf.start_message][step.step_name] = {
                "step_messaging_title": step_msg_conf.step_messaging_title,
                "bot_text": [text.text for text in step_messaging_model.StepMessagingText.objects.filter(step__id=step.id)],
                "media_first": True if step.send_first == "media" else False,
                "bot_media": {media.media_file.path: media.caption for media in step_messaging_model.StepMessagingMedia.objects.filter(step__id=step.id)},
                "user_buttons": [
                    {
                        button.button_1: button.type_button1, 
                        button.button_2: button.type_button2, 
                        button.button_3: button.type_button3
                    } for button in step_messaging_model.StepMessagingButtonsUser.objects.filter(step__id=step.id)
                ]
            }
            if list(step_messaging_model.StepMessagingStep.objects.filter(step_messaging_config__id=step_msg_conf.id))[-1] == step:
                bot_config["Step-Messaging"][step_msg_conf.start_message][step.step_name]["last_step"] = True
            else:
                bot_config["Step-Messaging"][step_msg_conf.start_message][step.step_name]["last_step"] = False
            
    
    # Generating a new config file for telegram bot
    with open('bot_engine/config.json', 'w') as config_file_w:
        json.dump(bot_config, config_file_w)


class BotAPI(models.Model):
    api = models.CharField(max_length=120, verbose_name="Telegram Bot API")
    
    class Meta:
        verbose_name = "API-key"
        verbose_name_plural = "API-key"

    def __str__(self):
        return "Edit Telegram Bot API-key"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        generate_bot_config()


class BotSettings(models.Model):
    non_stop = models.BooleanField(verbose_name="Should the bot be running all the time?", default=True)

    class Meta:
        verbose_name = "Bot settings"
        verbose_name_plural = "Bot settings"

    def __str__(self):
        return "Edit bot settings"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        generate_bot_config()


class AdminTelegramID(models.Model):
    admin_id = models.CharField(verbose_name="ID", max_length=20)

    class Meta:
        verbose_name = "Admin's telegram ID"
        verbose_name_plural = "Admin's telegram IDs"

    def __str__(self):
        return self.admin_id

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        generate_bot_config()
    
