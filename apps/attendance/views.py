from django.shortcuts import render
from django.views.generic import View
from apps.attendance.mixins import AttendanceGroupRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from apps.employee.models import Employee
from apps.attendance.models import Attendance
from django.urls import reverse
from django.contrib import messages

class AttendanceView(LoginRequiredMixin, AttendanceGroupRequiredMixin, View):
    def get(self, request):
        return render(request, 'attendance/attendance.html')
    
    def post(self, request):
        decoded_qr_text = request.POST.get('text')

        ## Check if QR code is not empty
        if not decoded_qr_text:
            return JsonResponse({'success':False, 'message': 'No QR code found'}, status=200)
        
        ## Check if QR code is valid email or employee_id
        try:
            # First try to find by email (for backward compatibility)
            employee = Employee.objects.get(email=decoded_qr_text)
        except Employee.DoesNotExist:
            try:
                # Then try to find by employee_id
                employee = Employee.objects.get(employee_id=decoded_qr_text)
            except Employee.DoesNotExist:
                return JsonResponse({'success':False, 'message': 'Employee not found'}, status=200)
        
        # Get today's date
        from django.utils import timezone
        import datetime
        
        today = timezone.now().date()
        # Fix the timezone issue by using make_aware
        today_start = timezone.make_aware(datetime.datetime.combine(today, datetime.time.min))
        today_end = timezone.make_aware(datetime.datetime.combine(today, datetime.time.max))
        
        # Rest of your code remains unchanged
        attendance_today = Attendance.objects.filter(
            employee=employee,
            created_at__range=(today_start, today_end)
        ).order_by('-created_at').first()
        
        # Check-in/check-out logic (unchanged)
        if not attendance_today:
            # No attendance today - create a Check In record
            Attendance.objects.create(
                employee=employee,
                status=Attendance.Status.CHECK_IN
            )
            message = 'Check-in recorded successfully'
        elif attendance_today.status == Attendance.Status.CHECK_IN:
            # Already checked in - create a Check Out record
            Attendance.objects.create(
                employee=employee,
                status=Attendance.Status.CHECK_OUT
            )
            message = 'Check-out recorded successfully'
        else:
            # Already checked out - inform the user
            message = 'You have already checked out today'
            return JsonResponse({'success':False, 'message': message}, status=200)
    
        return JsonResponse({
            'success': True, 
            'message': message,
            'redirect_url': f"{reverse('attendance_marked')}?message={message}"
        }, status=200)

    
    def attendance_marked(self, request):
        return render(request, 'attendance/attendance_marked.html')
    
class CustomLoginView(LoginView):
    template_name = 'attendance/login.html'
    redirect_authenticated_user = True
    
    def form_invalid(self, form):
        # Add a message to help debug
        messages.error(self.request, "Login failed. Please check your credentials.")
        return super().form_invalid(form)

class AttendanceMarkedView(LoginRequiredMixin, AttendanceGroupRequiredMixin, View):
    def get(self, request):
        message = request.GET.get('message', 'Attendance Marked Successfully!')
        return render(request, 'attendance/attendance_marked.html', {'message': message})
