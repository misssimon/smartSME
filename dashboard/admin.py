from django.contrib import admin
from .models import FarmerProfile, Product, Cart, CartItem

@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'farm_name', 'location', 'is_verified')
    list_filter = ('is_verified', 'location')
    search_fields = ('farm_name', 'user__username')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'farmer', 'price_per_unit', 'quantity_in_stock', 'discount_percentage', 'is_available')
    list_filter = ('is_available', 'unit', 'expiry_date')
    search_fields = ('name', 'farmer__username')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_items', 'total_price')
