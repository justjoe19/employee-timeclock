from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Employee
from .models import Punch
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
def employee_view(request):
    if request.method == 'POST':
        employee_id_parameter = request.POST.get("employee_id")

        if not employee_id_parameter.isdigit():
            messages.error(request, "Invalid employee number")
        else:
            try:
                employee = Employee.objects.get(employee_id=employee_id_parameter)
            except:
                messages.error(request, "Invalid employee number")
            else:
                try:
                    punches = []
                    for punch in list(Punch.objects.all()):
                        print(punch.employee_id)
                        if(punch.employee_id==int(employee.id)):
                            punches.append(punch)
                    print(employee_id_parameter,len(punches))
                    messages.success(request,f"Displaying clock in/out information for {employee.name}")
                    return render(request,"employeeView.html",{"punches":punches})
                except Employee.DoesNotExist:
                    messages.error(request,"Invalid employee number")
                else:
                    print("else")
    else:
        return render(request,"employeeView.html")
        