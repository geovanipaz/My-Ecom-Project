# Generated by Django 3.2.13 on 2022-05-14 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App_Login', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Designates whether the user shold be treatea is active', verbose_name='active'),
        ),
    ]
