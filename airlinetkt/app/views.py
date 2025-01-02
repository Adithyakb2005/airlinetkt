from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from .models import *
from .forms import FlightForm

# User Authentication Views
def user_register(req):
    if req.method=='POST':
        username=req.POST['uname']
        email=req.POST['email']
        pswd=req.POST['pswd']
        try:
            data=User.objects.create_user(first_name=username,email=email,username=email,password=pswd)
            data.save()
        except:
            messages.warning(req,"email already in use")
            return redirect(user_register)

        return redirect(user_login)
    else:
        return render(req,'user/register.html')
# def user_register(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#           # Use get() to avoid the error
#         if not username:
#             # Handle case where 'username' is not provided
#             return render(request, 'user/register.html', {'error': 'Username is required'})

#         # Other form handling logic (like password, email, etc.)
#         user = User.objects.create_user(username=username, password='your_password')
#         return redirect('user_login')
#     return render(request, 'user/register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request,user)
            return redirect(userhome)
        else:
            messages.error(request, "Invalid credentials.")
    return render(request, 'login.html')

def user_logout(request):
    auth_logout(request)
    return redirect(user_login)

# Admin Views
@login_required
def admin_home(request):
    flights=Flight.objects.all()
    bookings=Booking.objects.all()
    return render(request, 'admin/home.html',{'flights':flights,'bookings':bookings})

@login_required
def add_flight(request):
    if request.method == 'POST':
        form = FlightForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Flight added successfully!")
            return redirect(flight_list)
    else:
        form = FlightForm()
    return render(request, 'admin/add_flight.html', {'form': form})

@login_required
def flight_list(request):
    flights = Flight.objects.all()
    return render(request, 'admin/flight_list.html', {'flights': flights})

@login_required
def manage_bookings(request):
    bookings = Booking.objects.all()
    return render(request, 'admin/manage_bookings.html', {'bookings': bookings})

# User Views
@login_required
def userhome(request):
    flights = Flight.objects.filter(available_seats__gt=0)
    return render(request, 'user/userhome.html', {'flights': flights})

@login_required
def book_flight(request, flight_id,):
    flight = get_object_or_404(Flight, id=flight_id)
    with transaction.atomic():
        if flight.available_seats > 0:
            Booking.objects.create(user=request.passenger_name, flight=flight)
            flight.available_seats -= 1
            flight.save()
            messages.success(request, "Flight booked successfully!")
        else:
            messages.error(request, "No seats available.")
    return redirect(userhome)
def book_flight(request, flight_id):
    user = request.passenger_name  # Get the currently logged-in user
    flight = Flight.objects.get(id=flight_id)

    # Ensure user is passed correctly when creating the Booking object
    booking = Booking.objects.create(user=user, flight=flight)
    return redirect('some_view')


def save_profile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        # Save these details to the database or perform desired actions
        return HttpResponse("Profile updated successfully!")
    return HttpResponse("Invalid request")
