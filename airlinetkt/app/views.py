from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, Flight, Booking, Profile, ContactFormSubmission
from .forms import *

# --- User Authentication Views ---

def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('uname')
        email = request.POST.get('email')
        password = request.POST.get('pswd')

        if User.objects.filter(email=email).exists():
            messages.warning(request, "Email already in use.")
            return redirect('user_register')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Registration successful. Please log in.")
        return redirect('user_login')

    return render(request, 'user/register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            request.session['user'] = username
            return redirect('admin_home' if user.is_superuser else 'userhome')

        messages.error(request, "Invalid credentials.")

    return render(request, 'login.html')

def user_logout(request):
    auth_logout(request)
    # messages.success(request, "Logged out successfully.")
    return redirect('user_login')

# --- Admin Views ---

@login_required
def admin_home(request):
    flights = Flight.objects.all()
    bookings = Booking.objects.all()
    return render(request, 'admin/home.html', {'flights': flights, 'bookings': bookings})

@login_required
def add_flight(request):
    if request.method == 'POST':
        form = FlightForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('flight_list')
    else:
        form = FlightForm()

    return render(request, 'admin/add_flight.html', {'form': form})

@login_required
def flight_list(request):
    flights = Flight.objects.all()
    for flight in flights:
        flight.available_economy_seats = flight.economy_seats - Booking.objects.filter(flight=flight, class_type='Economy').count()
        flight.available_business_seats = flight.business_seats - Booking.objects.filter(flight=flight, class_type='Business').count()
        flight.available_first_class_seats = flight.first_class_seats - Booking.objects.filter(flight=flight, class_type='First Class').count()

    return render(request, 'admin/flight_list.html', {'flights': flights})

@login_required
def manage_bookings(request):
    bookings = Booking.objects.all()
    return render(request, "admin/manage_booking.html", {"bookings": bookings})
@login_required
def edit_flight(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    if request.method == 'POST':
        form = FlightForm(request.POST, instance=flight)
        if form.is_valid():
            form.save()
            return redirect('flight_list')  # Redirect to flight list
    else:
        form = FlightForm(instance=flight)
    return render(request, 'admin/edit_flight.html', {'form': form})
@login_required
def delete_flight(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    if request.method == 'POST':
        flight.delete()
        return redirect('flight_list') 
@login_required
def edit_booking(request, booking_id):
    # Fetch the booking or return 404 if not found
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            return redirect('manage_bookings')  # Redirect to booking management page after saving
    else:
        form = BookingForm(instance=booking)

    return render(request, 'admin/edit_booking.html', {'form': form, 'booking': booking})

@login_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.delete()
    return redirect('manage_bookings')

# --- User Views ---

@login_required
def userhome(request):
    flights = Flight.objects.all()
    return render(request, 'user/userhome.html', {'flights': flights})

def about(request):
    return render(request, 'user/about.html')

def contact(request):
    return render(request, 'user/contact.html')


def book_flight(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)

    if request.method == 'POST':
        passenger_name = request.POST.get('passenger_name')
        class_type = request.POST.get('class_type')
        date = request.POST.get('date')
        seats_requested = int(request.POST.get('seats', 1))

        with transaction.atomic():
            flight.refresh_from_db()

            available_seats = 0
            if class_type == 'Economy':
                available_seats = flight.economy_seats
            elif class_type == 'Business':
                available_seats = flight.business_seats
            elif class_type == 'First Class':
                available_seats = flight.first_class_seats

            if available_seats >= seats_requested:
                # Deduct the requested seats from the flight
                if class_type == 'Economy':
                    flight.economy_seats -= seats_requested
                elif class_type == 'Business':
                    flight.business_seats -= seats_requested
                elif class_type == 'First Class':
                    flight.first_class_seats -= seats_requested
                
                # Save updated flight seat counts
                flight.save()

                # Create booking entries for each seat requested
                for _ in range(seats_requested):
                    Booking.objects.create(
                        user=request.user,
                        flight=flight,
                        passenger_name=passenger_name,
                        class_type=class_type,
                        date=date,
                    )
                return redirect('userhome')

            else:
                return redirect('book_flight', flight_id=flight.id)

    return render(request, 'user/book_flight.html', {'flight': flight})


def view_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'user/view_bookings.html', {'bookings': bookings})
def view_ticket_details(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'user/ticket_details.html', {'booking': booking})
@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'user/profile.html', {'form': form})




@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Increment available seats based on the class type
    flight = booking.flight
    if booking.class_type == 'Economy':
        flight.economy_seats += 1
    elif booking.class_type == 'Business':
        flight.business_seats += 1
    elif booking.class_type == 'First Class':
        flight.first_class_seats += 1
    flight.save()

    # Delete booking and show message
    booking.delete()

    return redirect('view_bookings')

@csrf_exempt
def submit_form(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            email = request.POST.get('email')
            message = request.POST.get('message')

            if not name or not email or not message:
                return JsonResponse({'status': 'error', 'message': 'All fields are required.'}, status=400)

            ContactFormSubmission.objects.create(name=name, email=email, message=message)

            return JsonResponse({'status': 'success', 'message': 'Form submitted successfully!'}, status=200)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)
