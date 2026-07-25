from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('gifts/', views.gifts_view, name='gifts'),
    path('my-reservations/', views.my_reservations_view, name='my_reservations'),
    path('api/rsvp/', views.rsvp_api, name='api_rsvp'),
    path('api/gifts/<int:gift_id>/reserve/', views.reserve_api, name='api_reserve'),
    path('', views.home_view),
]
