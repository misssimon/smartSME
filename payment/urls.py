from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('mpesa/<str:order_number>/', views.mpesa_payment, name='mpesa_payment'),
    path('card/<str:order_number>/', views.card_payment, name='card_payment'),
    path('mpesa-callback/', views.mpesa_callback, name='mpesa_callback'),
    path('approve/<int:transaction_id>/', views.approve_payment, name='approve_payment'),
]