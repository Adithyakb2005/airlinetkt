from django.urls import path
from . import views

urlpatterns = [
    # User Authentication URLs
    path('', views.home, name='home'),
    path('searchflight',views.search_flights,name='search_flights'),
    path('login', views.user_login, name='user_login'),
    path('register/', views.user_register, name='user_register'),
    path('logout/', views.user_logout, name='user_logout'),

    # Admin URLs (requires login)
    path('admin_home/', views.admin_home, name='admin_home'),
    path('add_flight/', views.add_flight, name='add_flight'),
    path('flight_list/', views.flight_list, name='flight_list'),
    path('manage_bookings/', views.manage_bookings, name='manage_bookings'),
    path('edit_booking/<int:booking_id>/', views.edit_booking, name='edit_booking'),
    path('delete_booking/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    path('edit/<int:flight_id>/', views.edit_flight, name='edit_flight'),
    path('delete/<int:flight_id>/', views.delete_flight, name='delete_flight'),

    # User URLs (requires login)
    path('edit_profile/', views.edit_profile_view, name='edit_profile'),
    path('userhome/', views.userhome, name='userhome'),
    path('book_flight/<int:flight_id>/', views.book_flight, name='book_flight'),
    path('submit_form',views.submit_form),
    path('ticket/<int:booking_id>/', views.view_ticket_details, name='view_ticket_details'),
    # path('payment/<int:booking_id>/', views.payment_page, name='payment_page'),
    path('cancel_booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('profile/', views.profile_view, name='profile'),
    path('view_bookings/', views.view_bookings, name='view_bookings'),
    path('about/', views.about, name='about'),  # About page URL
    path('contact/', views.contact, name='contact'),

    # Booking Confirmation URL
    # path('booking_confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
]
