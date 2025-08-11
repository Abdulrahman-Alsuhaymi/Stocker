from django import forms
from .models import Supplier


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = [
            'name', 'email', 'phone', 'website',
            'country','logo', 'rating', 'notes'
        ]
        widgets = {
            'name' : forms.TextInput({"class" : "form-control"}),
            'email' : forms.EmailInput({"class" : "form-control"}),
            'phone' : forms.TextInput({"class" : "form-control"}),
            'website' : forms.URLInput({"class" : "form-control"}),
            'country' : forms.TextInput({"class" : "form-control"}),
            'logo' : forms.FileInput({"class" : "form-control"}),
            'rating' : forms.Select({"class" : "form-select"}),
            'notes' : forms.Textarea({"class" : "form-control"}),
        }