from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Farmer URLs
    path('farmer/', views.farmer_dashboard, name='farmer_dashboard'),
    path('farmer/add-product/', views.add_product, name='add_product'),
    path('farmer/edit-product/<int:pk>/', views.edit_product, name='edit_product'),
    path('farmer/delete-product/<int:pk>/', views.delete_product, name='delete_product'),
    path('farmer/profile/', views.farmer_profile, name='farmer_profile'),

    # Buyer URLs
    path('buyer/', views.buyer_dashboard, name='buyer_dashboard'),
    path('buyer/product/<int:pk>/', views.product_detail, name='product_detail'),
    path('buyer/add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('buyer/cart/', views.view_cart, name='view_cart'),
    path('buyer/cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('buyer/cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
]
