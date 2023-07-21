from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Employee, LOA
from .forms import TimeOffRequestForm
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
                employed = request.POST.get("employed")

                if employed == "True":
                    employee.punch()
                    punch_type = "Clock Out" if employee.is_clocked_in() else "Clock In"
                    current_time = datetime.datetime.now().strftime("%H:%M:%S")
                    messages.success(request, f"{employee.name}, your {punch_type.lower()} is at {current_time}")
                    return redirect('home')  # Assuming you have a URL name for the home page
                else:
                    messages.error(request, "Invalid input: Employee number is no longer employed")

    return render(request, 'clock_in_out.html')

def fire(request, employee_id):
    if request.method == 'POST':
        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            messages.error(request, "Invalid employee number")
        else:
            if employee.employed:
                employee.employed = False
                employee.save()
                messages.success(request, f"Employee with ID {employee_id} has been fired.")
            else:
                messages.error(request, "Employee is already not employed.")
        return redirect('home')  # Assuming you have a URL name for the home page

    return render(request, 'PLACEHOLDERfire.html')  # Replace 'PLACEHOLDERfire.html' with whichever appropriate template name

def add_deduct_pto(request, employee_id):
    if request.method == 'POST':
        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            messages.error(request, "Invalid employee number")
            return redirect('home')  # Assuming you have a URL name for the home page

        try:
            pto_change = int(request.POST.get("pto_change"))
        except ValueError:
            messages.error(request, "Invalid PTO change value. Please enter a valid integer.")
            return redirect('home')  # Assuming you have a URL name for the home page

        # Check if pto_change is positive (add PTO) or negative (deduct PTO)
        if pto_change > 0:
            employee.pto += pto_change
            action = "added"
        elif pto_change < 0:
            if employee.pto >= abs(pto_change):
                employee.pto += pto_change
                action = "deducted"
            else:
                messages.error(request, "Not enough PTO balance to deduct.")
                return redirect('home')  # Assuming you have a URL name for the home page
        else:
            messages.error(request, "Invalid PTO change value. Please enter a non-zero integer.")
            return redirect('home')  # Assuming you have a URL name for the home page

        employee.save()
        messages.success(request, f"Successfully {action} {abs(pto_change)} PTO for {employee.name}.")
        return redirect('home')  # Assuming you have a URL name for the home page

    return render(request, 'add_deduct_pto.html', {'employee_id': employee_id})

def submit_time_off_request(request, employee_id):
    employee = get_object_or_404(Employee, employee_id=employee_id)

    if request.method == 'POST':
        form = TimeOffRequestForm(request.POST, instance=LOA(employee=employee))

        if form.is_valid():
            form.save()
            messages.success(request, "Time off request submitted successfully.")
            return redirect('home')  # Assuming you have a URL name for the home page
    else:
        form = TimeOffRequestForm(instance=LOA(employee=employee))

    return render(request, 'submit_time_off_request.html', {'form': form})

def approve_deny_time_off_request(request, loa_id):
    loa = get_object_or_404(LOA, id=loa_id)

    if request.method == 'POST':
        approved = request.POST.get("approved") == "1"

        if loa.approved != approved:
            loa.approved = approved
            loa.save()

            if approved:
                messages.success(request, f"Time off request #{loa.id} approved.")
            else:
                messages.success(request, f"Time off request #{loa.id} denied.")
            return redirect('home')  # Assuming you have a URL name for the home page

    return render(request, 'PLACEHOLDERtimeoff_approved.html', {'loa': loa}) # Replace 'PLACEHOLDERtimeoff_approved.html' with whichever appropriate template name