from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Flight(models.Model):
    flight_number = models.CharField(max_length=10)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    available_seats = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    passenger_name = models.CharField(max_length=100)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('Confirmed', 'Confirmed'),('Cancelled', 'Cancelled'),])

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Failed', 'Failed')])
    date = models.DateTimeField(auto_now_add=True)
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    

