# Generated by Django 4.2 on 2025-05-30 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meeting_manager', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='meeting_number',
            field=models.CharField(max_length=50, null=True, unique=True, verbose_name='Số cuộc họp'),
        ),
    ]
