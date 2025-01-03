from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from .models import *
from .forms import *

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


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            # Check if the user is part of the 'admin' group
            if user.groups.filter(name='admin').exists():
                return redirect('admin_home')  # Redirect to admin dashboard
            else:
                return redirect('userhome')  # Redirect to user dashboard
        else:
            messages.error(request, "Invalid credentials.")
    return render(request, 'login.html')

def user_login(req):
    if 'admin' in req.session:
        return redirect(admin_home)
    if 'user' in req.session:
        return redirect(userhome)
    if req.method=='POST':
        username=req.POST['username']
        password=req.POST['password']
        data=authenticate(username=username,password=password)
        if data:
            login(req,data)
            if data.is_superuser:
                req.session['shop']=username #create
                return redirect(admin_home)
            else:
                req.session['user']=username 
                return redirect(userhome)
        else:
            messages.warning(req, "Invalid username or password.")
            return redirect(user_login)
    else:
        return render(req,'login.html')

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
    user_bookings = Booking.objects.filter(user=request.user)
    return render(request, 'user/userhome.html', {'flights': flights,'user_bookings': user_bookings,})

@login_required
def book_flight(request, flight_id):
    flight = Flight.objects.get(id=flight_id)

    
    if flight.available_seats > 0:
        
        booking = Booking.objects.create(
            user=request.user,
            flight=flight,
            passenger_name=request.user.username, 
            status='Confirmed'
        )

       
        return redirect('payment_page', booking_id=booking.id)

    else:
        messages.error(request, "Sorry, no available seats for this flight.")
        return redirect('userhome')

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
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    with transaction.atomic():
        if booking.status == 'Cancelled':
            messages.warning(request, "This booking is already cancelled.")
        else:
            
            booking.status = 'Cancelled'
            booking.save()
            
           
            booking.flight.available_seats += 1
            booking.flight.save()
            
            messages.success(request, "Your booking has been cancelled.")
    
    return redirect('userhome')  

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

    # Try to get the user's profile or create one if it doesn't exist
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        # Use the UserProfileForm with the existing profile instance
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()  # Save the updated or new profile data
            messages.success(request, 'Profile saved successfully!')
            return redirect('profile')  # Redirect to the profile page after save
    else:
        # Display the profile details in the form
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