from django import forms
from .models import *

class FlightForm(forms.ModelForm):
    class Meta:
        model = Flight
        fields = ['flight_number', 'origin', 'destination', 'departure_time', 'arrival_time', 'available_seats']
        widgets = {
            'departure_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'arrival_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
class PaymentForm(forms.Form):
    card_number = forms.CharField(max_length=16, widget=forms.TextInput(attrs={'placeholder': 'Enter Card Number', 'type': 'text'}))
    expiry_date = forms.CharField(max_length=5, widget=forms.TextInput(attrs={'placeholder': 'MM/YY', 'type': 'text'}))
    cvv = forms.CharField(max_length=3, widget=forms.TextInput(attrs={'placeholder': 'CVV', 'type': 'text'}))
    amount = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'readonly': 'readonly'}))

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'address', 'date_of_birth']
        # widgets = {
        #     'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        # }