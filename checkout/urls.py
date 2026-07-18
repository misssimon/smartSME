from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('success/<str:order_number>/', views.order_success, name='order_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('track/<str:order_number>/', views.track_order, name='track_order'),   # ← Add this
    path('company-registration/', views.company_registration, name='company_registration'),
    path('company-registration/success/', views.company_registration_success, name='company_registration_success'),
]