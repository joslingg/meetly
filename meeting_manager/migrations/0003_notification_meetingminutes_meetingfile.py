# Generated by Django 4.2 on 2025-05-30 03:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('meeting_manager', '0002_meeting_meeting_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('meeting_created', 'Cuộc hợp mới'), ('meeting_updated', 'Cập nhật cuộc họp'), ('meeting_reminder', 'Nhắc nhở cuộc họp')], max_length=40)),
                ('message', models.TextField(verbose_name='Nội dung thông báo')),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False, verbose_name='Đã đọc')),
                ('meeting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='meeting_manager.meeting', verbose_name='Cuộc họp')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL, verbose_name='Người nhận')),
            ],
            options={
                'verbose_name': 'Thông báo',
                'verbose_name_plural': 'Thông báo',
                'ordering': ['-sent_at'],
            },
        ),
        migrations.CreateModel(
            name='MeetingMinutes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='Nội dung biên bản')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_minutes', to=settings.AUTH_USER_MODEL, verbose_name='Thư ký')),
                ('meeting', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='minutes', to='meeting_manager.meeting', verbose_name='Cuộc họp')),
            ],
            options={
                'verbose_name': 'Biên bản cuộc họp',
                'verbose_name_plural': 'Biên bản cuộc họp',
            },
        ),
        migrations.CreateModel(
            name='MeetingFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='meeting_files/', verbose_name='Tệp đính kèm')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('meeting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='meeting_manager.meeting', verbose_name='Cuộc họp')),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uploaded_files', to=settings.AUTH_USER_MODEL, verbose_name='Người tải lên')),
            ],
            options={
                'verbose_name': 'Tệp đính kèm',
                'verbose_name_plural': 'Tệp đính kèm',
            },
        ),
    ]
