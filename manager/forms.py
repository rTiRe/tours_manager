from django import forms
from .models import Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = '__all__'
        widgets = {
            'entrance_number': forms.NumberInput(attrs={'min': 1, 'step': 1}),
            'floor': forms.NumberInput(attrs={'min': -1, 'step': 1}),
            'flat_number': forms.NumberInput(attrs={'min': 1, 'step': 1}),
        }