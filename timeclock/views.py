from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Employee
import datetime

def clock_in_out(request):
    if request.method == 'POST':
        employee_id = request.POST.get("employee_id")

        if not employee_id.isdigit():
            messages.error(request, "Invalid employee number")
        else:
            try:
                employee = Employee.objects.get(employee_id=employee_id)
            except Employee.DoesNotExist:
                messages.error(request, "Invalid employee number")
            else:
                employee.punch()
                punch_type = "Clock Out" if employee.is_clocked_in() else "Clock In"
                current_time = datetime.datetime.now().strftime("%H:%M:%S")
                messages.success(request, f"{employee.name}, your {punch_type.lower()} is at {current_time}")
                return redirect('home')  # Assuming you have a URL name for the home page

    return render(request, 'clock_in_out.html')
