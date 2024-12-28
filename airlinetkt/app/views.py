from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from .models import *
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

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

def userhome(req):
    return render(req, 'user/userhome.html')

def manage_bookings(request):
    bookings = Booking.objects.select_related('flight').all()  # Prefetch related flight data
    return render(request, 'flight_admin_home.html', {'bookings': bookings})

def edit_booking(request, id):
    booking = Booking.objects.get(pk=id)
    if request.method == 'POST':
        booking.passenger_name = request.POST.get('passenger_name', booking.passenger_name)
        booking.date = request.POST.get('date', booking.date)
        booking.save()
        return redirect('manage_bookings')
    return render(request, 'edit_booking.html', {'booking': booking})

def delete_booking(request, id):
    booking = Booking.objects.get(pk=id)
    booking.delete()
    return redirect('manage_bookings')

   