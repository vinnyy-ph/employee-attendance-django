from django.contrib import admin
from apps.employee.models import Employee

admin.site.site_header = 'Employee Management System'

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'created_at', 'updated_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    list_display_links = ('first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('id_card_photo',)  # Add this line to make id_card_photo read-only

admin.site.register(Employee, EmployeeAdmin)