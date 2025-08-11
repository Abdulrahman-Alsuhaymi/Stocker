from django import forms
from .models import Product, Category
from suppliers.models import Supplier


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label="CSV File")


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'sku', 'category', 'suppliers', 'cost_price', 
            'selling_price', 'current_stock', 'min_stock_level', 
            'image', 'is_perishable', 'expiry_date'
        ]
        widgets = {
            'name' : forms.TextInput({"class" : "form-control"}),
            'description' : forms.Textarea({"class" : "form-control"}),
            'sku' : forms.TextInput({"class" : "form-control"}),
            'category' : forms.Select({"class" : "form-select"}),
            'suppliers' : forms.SelectMultiple({"class" : "form-select"}),
            'cost_price' : forms.NumberInput({"class" : "form-control"}),
            'selling_price' : forms.NumberInput({"class" : "form-control"}),
            'current_stock' : forms.NumberInput({"class" : "form-control"}),
            'min_stock_level' : forms.NumberInput({"class" : "form-control"}),
            'image' : forms.FileInput({"class" : "form-control"}),
            'is_perishable' : forms.CheckboxInput({"class" : "form-check-input"}),
            'expiry_date' : forms.DateInput({"class" : "form-control", "type" : "date"}),
        }