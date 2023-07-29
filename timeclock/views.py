from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import models
from django.utils import timezone
from .models import Employee, LOA
from .forms import TimeOffRequestForm
from .models import Punch

from datetime import datetime
from datetime import date
import requests
from django.contrib.postgres.fields import DateRangeField

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
                employed = employee.employed

                if employed == True:
                    employee.punch()
                    punch_type = "Clock In" if employee.is_clocked_in() else "Clock Out"
                    current_time = datetime.now().strftime("%H:%M:%S")
                    messages.success(request, f"{employee.name}, your {punch_type.lower()} is at {current_time}")
                    
                    punches = []
                    PTOrequests=[]
                    if punch_type == "Clock In":
                        #collect punches for clock history. Wont let user edit them at all.
                        for punch in list(Punch.objects.all()):
                            if(punch.employee_id==int(employee.id)):
                                punches.append(punch)
                        #gather any submitted time off requests and make them viewable 
                        for LOAInstance in list(LOA.objects.all()):
                            if LOAInstance.employee==employee:
                                PTOrequests.append(LOAInstance)
                    

                   
                    #if no punches,no pto requests
                    if len(PTOrequests)==0 and len(punches)==0:
                        
                        return render(request, 'clock_in_out.html')
                    #there are punches,no pto requests
                    if len(PTOrequests)==0 and len(punches)>0:
                        
                        return render(request, 'clock_in_out.html',{"punches":punches})
                    #no punches, there are pto requests,
                    if len(PTOrequests)==0 and len(punches)>0:
                        
                        return render(request, 'clock_in_out.html',{"PTO":PTOrequests})
                    #there are punches and pto requests   
                    if len(PTOrequests)>0 and len(punches)>0:
                        return render(request, 'clock_in_out.html',{"punches":punches,"PTO":PTOrequests})
                else:
                    messages.error(request, "Invalid input: Employee number is no longer employed")

    return render(request, 'clock_in_out.html')
def employee_view(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            employee_id_parameter = request.POST.get("employee_id")

            if not employee_id_parameter.isdigit():
                messages.error(request, "Invalid employee number")
                return render(request,"employeeView.html")
            else:
                try:
                    employee = Employee.objects.get(employee_id=employee_id_parameter)
                except:
                    messages.error(request, "Invalid employee number")
                    return render(request,"employeeView.html")
                else:
                    try:
                        punches = []
                        PTOrequests = []
                        for punch in list(Punch.objects.all()):
                            if(punch.employee_id==int(employee.id)):
                                punches.append(punch)
                        for LOAInstance in list(LOA.objects.all()):
                            if LOAInstance.employee==employee:
                                PTOrequests.append(LOAInstance)
                        print(employee_id_parameter,len(punches))
                        messages.success(request,f"Displaying clock in/out information for {employee.name}")
                        return render(request,"employeeView.html",{"punches":punches,"PTO":PTOrequests})
                    except Employee.DoesNotExist:
                        messages.error(request,"Invalid employee number")
                    else:
                        print("else")
        else:
            return render(request,"employeeView.html")
    else:
         return render(request,"accessDenied.html")
        
def fire(request):
    if request.method == 'POST':
        try:
            employee = Employee.objects.get(employee_id=request.POST.get("employee_id"))
        except Employee.DoesNotExist:
            messages.error(request, "Invalid employee number")
        else:
            if employee.employed:
                employee.employed = not employee.employed
                employee.save()
                employee_id=request.POST.get("employee_id")
                messages.success(request, f"Employee with ID {employee_id} has been fired.")
            else:
                employee.employed = not employee.employed
                employee.save()
                messages.error(request, "Employee was already not employed. They have been re-hired.")
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
def pto_requests(request):
    return render(request,"pto_requests.html")
def submit_pto_request(request):
    employee = Employee.objects.get(employee_id=request.POST.get("employee_id"))
    requestStartStrs=request.POST.get("start_date").split("-")
    requestStart = date(int(requestStartStrs[0]),int(requestStartStrs[1]),int(requestStartStrs[2]))
    requestEndStrs=request.POST.get("end_date").split("-")
    requestEnd = date(int(requestEndStrs[0]),int(requestEndStrs[1]),int(requestEndStrs[2]))
    date_submitted = datetime.today().date()
    ptoRequest=LOA.objects.create(employee=employee,requestStart=requestStart,requestEnd=requestEnd,date_submitted=date_submitted,approved=False)
    ptoRequest.save()
    messages.success(request,"Successfully submitted PTO request.")
    return render(request, "pto_requests.html")