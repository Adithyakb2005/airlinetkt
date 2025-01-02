from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login),
    path('userhome/', views.userhome, name='userhome'),  # Correct name
    path('logout/', views.user_logout, name='user_logout'),
    path('register/', views.user_register),
    path('admin_home/', views.admin_home),
    path('add_flight/', views.add_flight, name='add_flight'),
    path('flight-list/', views.flight_list),
    path('manage-bookings/', views.manage_bookings),
    path('book_flight/<int:flight_id>/', views.book_flight, name='book_flight'),
    path('profile/', views.save_profile, name='profile'),
]
