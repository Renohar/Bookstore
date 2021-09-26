from django import forms
from django.forms import ModelForm
from django.db.models import fields
from django.forms import widgets
from core.models import *
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

class ProductForm(forms.ModelForm):

     class Meta:
        model = product
        fields = ['name','category_name','description','price','count','image']
        widgets ={
            'name' :forms.TextInput(attrs={'class':'ADDPRODUCT'}),
            'category_name' : forms.Select(attrs={'class':'ADDPRODUCT'}),
            'description': forms.Textarea(attrs={'class':'ADDPRODUCT'}),
            'price' : forms.NumberInput(attrs={'class':'ADDPRODUCT'}),
            'count' : forms.NumberInput(attrs={'class':'ADDPRODUCT'}),
            'image' : forms.FileInput(attrs={'class':'ADDPRODUCT'}),

        }

class CheckoutForm(forms.Form):

    streetaddress = forms.CharField(widget=forms.TextInput(attrs={
        'class' : 'form_control',
        'placeholder': '1234 Main St'
    }))
    apartmentaddress = forms.CharField(required=False,widget=forms.TextInput(attrs={
        'class' : 'form-control',
        'placeholder' : 'Apartment '
    }))
    country = CountryField(blank_label = '(select country)').formfield(widget =CountrySelectWidget(attrs={
        'class' : 'custom-select d-block w-100'   
    }))
    zipcode = forms.CharField(widget=forms.TextInput(attrs={
        'class' : 'form-control'
    }))
