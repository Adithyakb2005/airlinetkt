from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import *
from .forms import *

# --- User Authentication Views ---
def user_register(req):
    if req.method == 'POST':
        username = req.POST['uname']
        email = req.POST['email']
        pswd = req.POST['pswd']
        try:
            data = User.objects.create_user(first_name=username, email=email, username=email, password=pswd)
            data.save()
        except:
            messages.warning(req, "Email already in use.")
            return redirect(user_register)

        return redirect(user_login)
    else:
        return render(req, 'user/register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if user.groups.filter(name='admin').exists():
                return redirect('admin_home')
            else:
                return redirect('userhome')
        else:
            messages.error(request, "Invalid credentials.")
    return render(request, 'login.html')


def user_logout(request):
    auth_logout(request)
    return redirect(user_login)


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
            return redirect(flight_list)
    else:
        form = FlightForm()
    return render(request, 'admin/add_flight.html', {'form': form})


@login_required
def flight_list(request):
    flights = Flight.objects.all()

    for flight in flights:
        # Assuming you have a Booking model with class_type field
        flight.available_economy_seats = flight.economy_seats - Booking.objects.filter(flight=flight, class_type='Economy').count()
        flight.available_business_seats = flight.business_seats - Booking.objects.filter(flight=flight, class_type='Business').count()
        flight.available_first_class_seats = flight.first_class_seats - Booking.objects.filter(flight=flight, class_type='First Class').count()

    return render(request, 'admin/flight_list.html', {'flights': flights})


@login_required
def manage_bookings(request):
    bookings = Booking.objects.all()
    return render(request, 'admin/manage_bookings.html', {'bookings': bookings})


# --- User Views ---
@login_required
def userhome(request):
    flights = Flight.objects.filter(available_seats__gt=0)
    user_bookings = Booking.objects.filter(user=request.user)
    return render(request, 'user/userhome.html', {'flights': flights, 'user_bookings': user_bookings})


@login_required
def book_flight(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)

    if request.method == 'POST':
        if flight.book_seat():
            booking = Booking.objects.create(
                passenger_name=request.POST['passenger_name'],
                flight=flight,
                price=flight.price,
                date=request.POST['date']
            )
            return redirect('booking_confirmation', booking_id=booking.id)
        else:
            error_message = "Sorry, no available seats for this flight."
            return render(request, 'book_ticket.html', {'flight': flight, 'error_message': error_message})

    return render(request, 'book_ticket.html', {'flight': flight})


@login_required
def payment_page(request, booking_id):
    booking = Booking.objects.get(id=booking_id)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            transaction_id = "TXN" + str(booking.id)
            payment = Payment.objects.create(
                user=request.user,
                booking=booking,
                amount=booking.flight.price,
                transaction_id=transaction_id,
                payment_status="Completed"
            )
            booking.status = "Paid"
            booking.save()

            messages.success(request, "Payment successful!")
            return redirect('userhome')
    else:
        form = PaymentForm(initial={'amount': booking.flight.price})

    return render(request, 'user/payment.html', {'form': form, 'booking': booking})


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    flight = booking.flight
    flight.cancel_seat()
    booking.delete()
    return redirect('manage_bookings')


@login_required
def edit_profile(request):
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        user.username = username
        user.email = email
        user.save()

        if profile:
            profile.phone = phone
            profile.address = address
            profile.save()
        else:
            Profile.objects.create(user=user, phone=phone, address=address)

        messages.success(request, "Profile updated successfully.")
        return redirect('edit_profile')

    return render(request, 'edit_profile.html', {
        'user': user,
        'profile': profile,
    })


@login_required
def profile_view(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile saved successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'user/profile.html', {
        'form': form,
        'profile': profile,
    })


@login_required
def buy_ticket(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)

    if flight.available_seats > 0:
        Booking.objects.create(
            user=request.user,
            flight=flight,
            status="Confirmed",
            date=flight.departure_time.date()
        )
        flight.available_seats -= 1
        flight.save()

        messages.success(request, f"Your ticket for flight {flight.flight_number} has been booked successfully!")
        return redirect('userhome')
    else:
        messages.error(request, f"Sorry, no available seats for flight {flight.flight_number}.")
        return redirect('userhome')


# --- Booking Confirmation View ---
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.status == "Confirmed":
        messages.success(request, f"Your booking for flight {booking.flight.flight_number} has been confirmed!")
    else:
        messages.error(request, "There was an issue with your booking confirmation.")

    return render(request, 'user/booking_confirmation.html', {'booking': booking})
