from django import forms
from .models import DeliveryCompany


class CompanyRegistrationForm(forms.ModelForm):
    class Meta:
        model = DeliveryCompany
        fields = ['name', 'description', 'logo', 'contact_phone', 'contact_email', 'website']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'name': 'Company Name',
            'contact_phone': 'Contact Phone Number',
            'contact_email': 'Contact Email',
        }
