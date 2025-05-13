from django.contrib import admin
from apps.employee.models import Employee

admin.site.site_header = 'Employee Management System'

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'first_name', 'last_name', 'email', 'designation', 'phone', 'created_at', 'updated_at')
    search_fields = ('employee_id', 'first_name', 'last_name', 'email', 'phone')
    list_display_links = ('employee_id', 'first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('id_card_photo',)

admin.site.register(Employee, EmployeeAdmin)