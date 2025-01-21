from django import forms
from .models import *

class FlightForm(forms.ModelForm):
    class Meta:
        model = Flight
        fields = ['flight_number', 'origin', 'destination', 'departure_time', 'arrival_time','economy_seats','business_seats','first_class_seats','economy_price','business_price','first_class_price','available_seats' ]
        widgets = {
            'departure_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'arrival_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['passenger_name', 'flight', 'status','class_type']
    CLASS_TYPE_CHOICES = [
        ('economy', 'Economy'),
        ('business', 'Business'),
        ('first', 'First Class'),
    ]

    class_type= forms.ChoiceField(choices=CLASS_TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
class PaymentForm(forms.Form):
    card_number = forms.CharField(max_length=16, widget=forms.TextInput(attrs={'placeholder': 'Enter Card Number', 'type': 'text'}))
    expiry_date = forms.CharField(max_length=5, widget=forms.TextInput(attrs={'placeholder': 'MM/YY', 'type': 'text'}))
    cvv = forms.CharField(max_length=3, widget=forms.TextInput(attrs={'placeholder': 'CVV', 'type': 'text'}))
    amount = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'readonly': 'readonly'}))

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'address', 'date_of_birth']
        widgets = {
                'phone': forms.TextInput(attrs={'class': 'form-control'}),
                'address': forms.TextInput(attrs={'class': 'form-control'}),
                'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            }
        
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'address','date_of_birth']