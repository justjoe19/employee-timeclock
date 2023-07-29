from django.contrib import admin
from .models import Employee, Punch,LOA

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'employee_id')

admin.site.register(Punch)
admin.site.register(LOA)

