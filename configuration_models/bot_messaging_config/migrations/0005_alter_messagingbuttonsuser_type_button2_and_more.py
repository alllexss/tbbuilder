# Generated by Django 4.1 on 2022-08-21 04:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_messaging_config', '0004_messagingbuttonsuser_type_button1_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messagingbuttonsuser',
            name='type_button2',
            field=models.CharField(blank=True, choices=[('text', 'Text button'), ('location', 'Ask location'), ('phone', 'Ask phone number')], default='text', max_length=20, verbose_name='Button №2 type'),
        ),
        migrations.AlterField(
            model_name='messagingbuttonsuser',
            name='type_button3',
            field=models.CharField(blank=True, choices=[('text', 'Text button'), ('location', 'Ask location'), ('phone', 'Ask phone number')], default='text', max_length=20, verbose_name='Button №3 type'),
        ),
    ]
