from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponseBadRequest
from .models import *
from .forms import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


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

        if user is not None:
            login(request, user)
            request.session['user'] = username
            return redirect('admin_home' if user.is_superuser else 'userhome')

        messages.error(request, "Invalid credentials.")

    return render(request, 'login.html')

def user_logout(request):
    auth_logout(request)
    messages.success(request, "Logged out successfully.")
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
            messages.success(request, "Flight added successfully!")
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

# --- User Views ---
@login_required
def userhome(request):
    flights = Flight.objects.all()
    return render(request, 'user/userhome.html', {'flights': flights})

def about(request):
    return render(request, 'user/about.html')

def contact(request):
    return render(request, 'user/contact.html')
def edit_booking(request, booking_id):
    """
    View to edit an existing booking.
    """
    # Fetch the booking object or return a 404 if not found
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        # Bind form with POST data
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, "Booking updated successfully.")
            return redirect('admin_home')  # Redirect to admin homepage
        else:
            messages.error(request, "Failed to update booking. Please check the details.")
    else:
        # Populate form with the current booking data
        form = BookingForm(instance=booking)

    return render(request, 'admin/edit_booking.html', {'form': form, 'booking': booking})
def delete_booking(request, booking_id):
    """
    View to delete a booking.
    """
    # Fetch the booking object or return a 404 error
    booking = get_object_or_404(Booking, id=booking_id)

    # Delete the booking
    booking.delete()

    # Display a success message and redirect to manage bookings
    messages.success(request, "Booking deleted successfully.")
    return redirect('manage_bookings')
@login_required
def book_flight(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)

    if request.method == 'POST':
        passenger_name = request.POST.get('passenger_name')
        class_type = request.POST.get('class_type')
        date = request.POST.get('date')

        if class_type == 'Economy' and flight.economy_seats <= 0:
            messages.error(request, "No economy seats available.")
        elif class_type == 'Business' and flight.business_seats <= 0:
            messages.error(request, "No business seats available.")
        elif class_type == 'First Class' and flight.first_class_seats <= 0:
            messages.error(request, "No first-class seats available.")
        else:
            Booking.objects.create(
                user=request.user,
                flight=flight,
                passenger_name=passenger_name,
                class_type=class_type,
                date=date,
            )
            messages.success(request, "Flight booked successfully!")
            return redirect('userhome')

    return render(request, 'user/book_flight.html', {'flight': flight})
  
def view_bookings(request):
    # Retrieve all bookings made by the logged-in user
    flights=Flight.objects.all()
    bookings = Booking.objects.filter(user=request.user)

    # Render the template with the bookings context
    return render(request, 'user/view_bookings.html', {'flights':flights,'bookings': bookings})
def profile_view(request):
    return render(request, 'user/profile.html', {'user': request.user})

@login_required
def edit_profile(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        user.username = username
        user.email = email
        user.save()

        profile.phone = phone
        profile.address = address
        profile.save()

        messages.success(request, "Profile updated successfully.")
        return redirect('edit_profile')

    return render(request, 'user/edit_profile.html', {'user': user, 'profile': profile})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.delete()
    messages.success(request, "Booking canceled successfully.")
    return redirect('manage_bookings')
@csrf_exempt  # Allows POST requests without CSRF token for simplicity (use cautiously in production)
def submit_form(request):
    if request.method == 'POST':
        try:
            # Parse the incoming data
            name = request.POST.get('name')
            email = request.POST.get('email')
            message = request.POST.get('message')

            # Validate the data (optional, depends on your requirements)
            if not name or not email or not message:
                return JsonResponse({'status': 'error', 'message': 'All fields are required.'}, status=400)

            # Save the data to the database
            ContactFormSubmission.objects.create(name=name, email=email, message=message)

            # Respond with success
            return JsonResponse({'status': 'success', 'message': 'Form submitted successfully!'}, status=200)

        except Exception as e:
            # Handle unexpected errors
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # Return an error for unsupported HTTP methods
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)