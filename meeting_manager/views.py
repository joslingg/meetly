from django.shortcuts import render,redirect,get_list_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Department, Organization, UserAffiliation, Meeting
from .forms import MeetingFilterForm
from django.db.models import Q

def meeting_list(request):
    """
    Hiển thị danh sách các cuộc họp.
    """
    filter_form = MeetingFilterForm(request.GET)
    meetings = Meeting.objects.all()
    
    if filter_form.is_valid():
        start_date = filter_form.cleaned_data.get('start_date')
        end_date = filter_form.cleaned_data.get('end_date')
        department = filter_form.cleaned_data.get('department')
        organization = filter_form.cleaned_data.get('organization')
        status = filter_form.cleaned_data.get('status')
        search = filter_form.cleaned_data.get('search')
        
        if start_date:
            meetings = meetings.filter(date__gte=start_date)
        if end_date:
            meetings = meetings.filter(date__lte=end_date)
        if department:
            meetings = meetings.filter(departments=department)
        if organization:
            meetings = meetings.filter(organizations=organization)
        if status:
            meetings = meetings.filter(status=status)
        if search:
            meetings = meetings.filter(
                Q(meeting_number__iconstains=search) |
                Q(title__icontains=search) |
                Q(host__icontain=search)
            )
            
    #Group các cuộc họp theo ngày
    meetings = meetings.order_by('-date','-time')
    context = {
        'meetings':meetings,
        'filter_form':filter_form,
    }
    
    return render(request, 'meeting_manager/meeting_list.html',context)
