from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login),
    path('userhome/', views.userhome, name='userhome'),  # Correct name
    path('logout/', views.user_logout, name='user_logout'),
    path('register/', views.user_register),
    path('admin_home/', views.admin_home, name='admin_home'),
    path('add_flight/', views.add_flight, name='add_flight'),
    path('flight-list/', views.flight_list),
    path('payment/<int:booking_id>/', views.payment_page, name='payment_page'),
    path('manage_bookings/', views.manage_bookings),
    path('book_flight/<int:flight_id>/', views.book_flight, name='book_flight'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('buy-ticket/<int:flight_id>/', views.buy_ticket, name='buy_ticket'),
    path('profile/',views. profile_view, name='profile'),
]
