from django import forms
from django.utils import timezone
from .models import LOA

class TimeOffRequestForm(forms.ModelForm):
    class Meta:
        model = LOA
        fields = ['request', 'time_submitted']

    def clean_request(self):
        request = self.cleaned_data['request']
        start_date, end_date = request.lower, request.upper

        # Calculate the number of days in the request
        num_days = (end_date - start_date).days + 1

        # Check if the request covers at least 8 hours per day
        if num_days * 8 > self.instance.employee.pto:
            raise forms.ValidationError("Insufficient PTO balance to cover the request. Please adjust the dates or request fewer days.")

        return request