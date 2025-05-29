from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Tên Khoa / Phòng')
    description = models.TextField(blank=True, null=True, verbose_name='Mô tả')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Khoa / Phòng'
        verbose_name_plural = 'Khoa / Phòng'
    
    def __str__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        if self.meetings.exists():
            raise ValueError("Không thể xoá Khoa/Phòng này vì đã có cuộc họp được tổ chức.")
        super().delete(**args, **kwargs)

class Organization(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Tên Tổ chức')
    description = models.TextField("Mô tả", blank=True, null=True)
    
    def __str__(self):
        return self.name
    
class UserAffiliation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='affiliations',
        verbose_name='Người dùng'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='affiliations',
        verbose_name='Khoa / Phòng',
        blank=True, null=True,
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='affiliations',
        verbose_name='Tổ chức',
        blank=True, null=True,
    )
    role = models.CharField("Vai trò", max_length=100, blank=True, null=True)
    is_active = models.BooleanField("Đang hoạt động", default=True)
    
    class Meta:
        verbose_name = "Ban/Ngành công tác"
        verbose_name_plural = "Ban/Ngành công tác"
    
    def __str__(self):
        affiliation = []
        if self.department:
            affiliation.append(f"{self.role} - {self.department.name}")
        if self.organization:
            affiliation.append(f"{self.role} - {self.organization.name}")
        return ", ".join(affiliation)
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='Người dùng')
    zalo_id = models.CharField("Zalo ID", max_length=100, blank=True, null=True)
    phone_number = models.CharField("Số điện thoại", max_length=15, blank=True, null=True)
    zalo_notification = models.BooleanField("Nhận thông báo qua Zalo", default=True)

    def __str__(self):
        return f"Hồ sơ của {self.user.get_full_name()}"
    
class MeetingParticipant(models.Model):
    PARTICIPANT_TYPE = [
        ('individual','Cá nhân'),
        ('department','Khoa/Phòng'),
        ('group','Ban/Đoàn thể'),
    ]
    
    meeting = models.ForeignKey(
        'Meeting',
        on_delete=models.CASCADE,
        related_name='meeting_participants',
        verbose_name='Cuộc họp'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='meeting_participants',
        verbose_name='Cá nhân', blank=True, null=True
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='meeting_participants',
        verbose_name='Khoa/Phòng', blank=True, null=True
    )
    participant_type = models.CharField(
        max_length=20,
        choices=PARTICIPANT_TYPE,
        default='individual',
        verbose_name='Loại thành phần tham dự'
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='meeting_participants',
        verbose_name='Tổ chức', blank=True, null=True
    )
    is_required = models.BooleanField("Bắt buộc tham dự", default=True)
    attended = models.BooleanField("Đã tham dự", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_participants',
        verbose_name='Người tạo'
    )
    
    class Meta:
        verbose_name = 'Thành phần tham dự cuộc họp'
        verbose_name_plural = 'Thành phần tham dự cuộc họp'

    def __str__(self):
        if self.user:
            return f"{self.user.get_full_name()} - {self.get_participant_type_display()}"
        elif self.department:
            return f"{self.department.name} - {self.get_participant_type_display()}"
        elif self.organization:
            return f"{self.organization.name} - {self.get_participant_type_display()}"
        return f"Thành phần tham dự - {self.get_participant_type_display()}"
    
    def clean(self):
        if self.participant_type == 'individual' and not self.user:
            raise ValidationError('Cá nhân tham dự phải có user')
        if self.participant_type == 'department' and not self.department:
            raise ValidationError('Khoa/Phòng tham dự phải được khai báo')
        if self.participant_type == 'group' and not self.organization:
            raise ValidationError('Ban/Đoàn thể tham dự phải được khai báo')

    def send_notification(self):
        if self.user.profile.zalo_notification and self.user.profile.zalo_id:
            self.send_notification_via_zalo()
    
    def send_notification_via_zalo(self):
        pass
    
    
class Meeting(models.Model):
    status_choices = [
        ('Đã lên lịch', 'Đã lên lịch'),
        ('Đang diễn ra', 'Đang diễn ra'),
        ('Đã kết thúc', 'Đã kết thúc'),
        ('Bị hủy', 'Bị hủy'),
    ]
    
    title = models.CharField("Nội dung", max_length=255)
    date = models.DateField("Ngày họp")
    time = models.TimeField("Thời gian", blank=True, null=True)
    preparation = models.ForeignKey(User, on_delete=models.CASCADE, related_name='preparation_meetings', verbose_name='Người chuẩn bị', blank=True, null=True)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_meetings', verbose_name='Chủ trì')
    
    participants = models.ManyToManyField(
        MeetingParticipant,
        related_name='meetings',
        verbose_name='Thành phần tham dự',
        blank=True
    )

    def add_participant(self, user, participant_type='individual', department=None, organization=None, is_required=True):
        participant = MeetingParticipant.objects.create(
            meeting=self,
            user=user,
            participant_type=participant_type,
            organization = organization,
            department=department,
            is_required=is_required
        )
        participant.send_notification()
        return participant

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_meetings',
        verbose_name='Người tạo'
    )
    location = models.CharField("Địa điểm", max_length=255, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=status_choices,
        default='Đã lên lịch',
        verbose_name='Trạng thái'
    )
    
    class Meta:
        ordering = ['-date', '-time']
        verbose_name = 'Cuộc họp'
        verbose_name_plural = 'Cuộc họp'
    
    def __str__(self):
        return f"{self.title} - {self.date} {self.time if self.time else ''}"