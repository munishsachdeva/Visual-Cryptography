# Generated by Django 3.2.16 on 2023-01-18 13:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0006_alter_captcha_voter'),
    ]

    operations = [
        migrations.RenameField(
            model_name='captcha',
            old_name='share_2',
            new_name='share_1',
        ),
    ]
