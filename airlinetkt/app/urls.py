from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),  # Updated view name
    path('logout/', views.logout, name='logout'),
    path('adminhome', views.home, name='home'),
    path('add_flight/', views.add_flight, name='add_flight'),
    path('add_flight/', views.add_flight, name='add_flight'),
    path('flights/', views.flight_list, name='flight_list'), 
    path('manage_bookings/', views.manage_bookings, name='manage_bookings'),
    path('edit_flight/<int:id>/', views.edit_flight, name='edit_flight'),
    path('delete_booking/<int:id>/', views.delete_flight, name='delete_booking'),

    path('register/', views.register, name='register'),
    path('userhome/', views.userhome, name='userhome'),
    path('book/<int:flight_id>/', views.book_flight, name='book_flight'),
]
