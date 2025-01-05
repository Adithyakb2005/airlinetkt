from django.urls import path
from . import views

urlpatterns = [
    # User Authentication URLs
    path('', views.user_login, name='user_login'),
    path('register/', views.user_register, name='user_register'),
    path('logout/', views.user_logout, name='user_logout'),

    # Admin URLs (requires login)
    path('admin_home', views.admin_home, name='admin_home'),
    path('add_flight/', views.add_flight, name='add_flight'),
    path('flight_list/', views.flight_list, name='flight_list'),
    path('manage_bookings/', views.manage_bookings, name='manage_bookings'),
    path('edit_booking/<int:id>/', views.edit_booking, name='edit_booking'),
    path('delete_booking/<int:id>/', views.delete_booking, name='delete_booking'),
    # User URLs (requires login)
    path('userhome/', views.userhome, name='userhome'),
    path('book_flight/<int:flight_id>/', views.book_flight, name='book_flight'),
    path('payment/<int:booking_id>/', views.payment_page, name='payment_page'),
    path('cancel_booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('profile/', views.profile_view, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),

    # Example of a dynamic URL for booking confirmation
    path('booking_confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
]
