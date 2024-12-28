from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),  # Updated view name
    path('logout/', views.logout, name='logout'),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('userhome/', views.userhome, name='userhome'),
    path('manage_bookings/', views.manage_bookings, name='manage_bookings'),
    path('edit_booking/<int:id>/', views.edit_booking, name='edit_booking'),
    path('delete_booking/<int:id>/', views.delete_booking, name='delete_booking'),
]
