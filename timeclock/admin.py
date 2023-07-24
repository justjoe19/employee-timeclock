from django.contrib import admin
from .models import Employee, Punch

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'employee_id')

admin.site.register(Punch)

