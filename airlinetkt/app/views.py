from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from .models import *
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .forms import FlightForm

# Create your views here.

def user_login(req):
    if 'admin' in req.session:
        return redirect(home)
    if 'user' in req.session:
        return redirect(userhome)
    if req.method == 'POST':
        username = req.POST['username']
        password = req.POST['password']
        data = authenticate(username=username, password=password)
        if data:
            auth_login(req, data)  # Use the imported auth_login here
            if data.is_superuser:
                req.session['admin'] = username  # create
                return redirect(home)
            else:
                req.session['user'] = username
                return redirect(userhome)
        else:
            messages.warning(req, "Invalid username or password.")
            return redirect(user_login)  # Redirect to the updated function
    else:
        return render(req, 'login.html')

def logout(req):
    auth_logout(req)  # Use the imported auth_logout here
    req.session.flush()
    return redirect(user_login)  # Redirect to the updated login view

#---------------------admin------------------------

def home(request):
    return render(request, 'admin/home.html')

def register(req):
    if req.method == 'POST':
        uname = req.POST.get('uname')  # Safely get form values
        email = req.POST.get('email')
        pswd = req.POST.get('pswd')

        # Validate form inputs
        if not uname or not email or not pswd:
            messages.error(req, "All fields are required.")
            return redirect('register')  # Use the URL name for redirection

        try:
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                messages.warning(req, "Email already in use.")
                return redirect('register')

            # Create the user
            data = User.objects.create_user(username=email, email=email, password=pswd, first_name=uname)
            data.save()
            messages.success(req, "Registration successful! Please log in.")
            return redirect('login')  # Redirect to the login page
        except Exception as e:
            messages.error(req, f"An error occurred: {e}")
            return redirect('register')

    else:
        return render(req, 'user/register.html')

# ----------addflight-----------
def add_flight(request):
    if request.method == 'POST':
        form = FlightForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('flight_list')  # Redirect to a page listing all flights
    else:
        form = FlightForm()
    return render(request, 'admin/add_flight.html', {'form': form})

def flight_list(request):
    flights = Flight.objects.all()  # Fetch all flights
    return render(request, 'admin/flight_list.html', {'flights': flights})

def manage_bookings(request):
    bookings = Booking.objects.select_related('flight').all()  # Prefetch related flight data
    return render(request, 'flight_admin_home.html', {'bookings': bookings})

def edit_flight(request, id):
    flight = Flight.objects.get(pk=id)
    if request.method == 'POST':
        # Update flight details here
        flight.flight_number = request.POST['flight_number']
        flight.origin = request.POST['origin']
        flight.destination = request.POST['destination']
        flight.departure_time = request.POST['departure_time']
        flight.arrival_time = request.POST['arrival_time']
        flight.available_seats = request.POST['available_seats']
        flight.save()
        return redirect('all_flights')  # Or your specific page after editing

    return render(request, 'edit_flight.html', {'flight': flight})


def delete_flight(request, id):
    flight = Flight.objects.get(pk=id)
    flight.delete()
    return redirect('all_flights')  # Or your specific page after deleting

# --------------user---------
def userhome(request):
    flights = Flight.objects.filter(available_seats__gt=0)  # Only flights with available seats
    user_bookings = Booking.objects.filter(user=request.user)

    return render(request, 'user/userhome.html', {'flights': flights,'user_bookings': user_bookings})

def book_flight(request, flight_id):
    flight = Flight.objects.get(id=flight_id)
    if flight.available_seats > 0:
        Booking.objects.create(user=request.user, flight=flight, status='Confirmed')
        flight.available_seats -= 1
        flight.save()
    return redirect('userhome')
