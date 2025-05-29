from django import forms
from .models import Department, Organization, Meeting, MeetingParticipant, UserAffiliation
from django.contrib.auth.models import User
from datetime import date as dt_date, time as dt_time

class DateInput(forms.DateInput):
    input_type = 'date'
    
class TimeInput(forms.TimeInput):
    input_type = 'time'
    
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên Khoa / Phòng'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Nhập mô tả'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            
class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên Tổ chức'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Nhập mô tả'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            
class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = [
            'title',
            'date',
            'time',
            'preparation',
            'host',
            'location',
            'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Nhập tiêu đề cuộc họp'}),
            'date': DateInput(attrs={'class': 'form-control','placeholder': 'Chọn ngày'}),
            'time': TimeInput(attrs={'class': 'form-control','placeholder': 'Chọn giờ'}),
            'preparation': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Chọn người chuẩn bị'}),
            'host': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Chọn người chủ trì'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập địa điểm'}),
            'status': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Chọn trạng thái'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        # Lấy danh sách user cho preparation và host
        self.fields['preparation'].queryset = User.objects.all()
        self.fields['host'].queryset = User.objects.all()
        # Thêm các label tiếng việt
        self.fields['title'].label = 'Nội dung'
        self.fields['date'].label = 'Ngày họp'
        self.fields['time'].label = 'Thời gian'
        self.fields['preparation'].label = 'Người chuẩn bị'
        self.fields['host'].label = 'Chủ trì'
        self.fields['location'].label = 'Địa điểm'
        self.fields['status'].label = 'Trạng thái'
        
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        
        if date and time:
            # Kiểm tra xem ngày và giờ có hợp lệ không
            if date < dt_date(2025,1,1):
                self.add_error('date', 'Ngày họp không hợp lệ.')
            if time < dt_time(0,0):
                self.add_error('time', 'Thời gian họp không hợp lệ.')
                
        participant_type = cleaned_data.get('participant_type')
        user = cleaned_data.get('user')
        department = cleaned_data.get('department')
        organization = cleaned_data.get('organization')
        
        if participant_type == 'individual' and not user:
            self.add_error('user', 'Vui lòng chọn người tham dự cá nhân.')
        elif participant_type == 'department' and not department:
            self.add_error('department', 'Vui lòng chọn Khoa / Phòng tham dự.')
        elif participant_type == 'organization' and not organization:
            self.add_error('organization', 'Vui lòng chọn Ban/Ngành tham dự.')

        return cleaned_data

class MeetingParticipantForm(forms.ModelForm):
    class Meta:
        model = MeetingParticipant
        fields = [
            'participant_type',
            'user',
            'department',
            'organization',
            'participant_type',
            'is_required',
        ]
        
        widgets = {
            'participant_type': forms.Select(attrs={'class':'form-control','placeholder':'Chọn loại thành phần tham dự'}),
            'user': forms.Select(attrs={'class':'form-control','placeholder':'Chọn cá nhân tham dự'}),
            'department': forms.Select(attrs={'class':'form-control','placeholder':'Chọn Khoa / Phòng tham dự'}),
            'organization': forms.Select(attrs={'class':'form-control','placeholder':'Chọn Ban/Ngành tham dự'}),
            'is_required': forms.CheckboxInput(attrs={'class':'form-check-input'}),
        }
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args, **kwargs)
        # Lấy danh sách user cho trường user
        self.fields['user'].queryset = User.objects.all()
        # Lấy danh sách department cho trường department
        self.fields['department'].queryset = Department.objects.all()
        # Lấy danh sách organization cho trường organization
        self.fields['organization'].queryset = Organization.objects.all()
        
        # Thêm các label tiếng việt
        self.fields['participant_type'].label = 'Loại thành phần tham dự'
        self.fields['user'].label = 'Cá nhân tham dự'
        self.fields['department'].label = 'Khoa / Phòng tham dự'
        self.fields['organization'].label = 'Ban/Ngành tham dự'
        self.fields['is_required'].label = 'Bắt buộc tham dự'

MeetingParticipantFormSet = forms.modelformset_factory(
    Meeting, #Model cha
    MeetingParticipant, #Model con
    form = MeetingParticipantForm, #Form con
    extra=1, #Thêm một form trống để người dùng có thể thêm thành phần tham dự mới
    can_delete=True, #Cho phép xóa thành phần tham dự
)

# Form kết hợp Meeting và MeetingParticipant
class MeetingWithParticipantsForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = [
            'title',
            'date',
            'time',
            'preparation',
            'host',
            'location',
            'status',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.participant_formset = MeetingParticipantFormSet(
            instance = self.instance,
            data = self.data if self.is_bound else None,
            files = self.files if self.is_bound else None,
        )
    def is_valid(self):
        return super().is_valid() and self.participant_formset.is_valid()
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.participant_formset.instance = instance
            self.participant_formset.save()
        return instance