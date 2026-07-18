from django.contrib import admin
from .models import (
    DeliveryCompany, DeliveryPerson, DeliveryOption, 
    Order, OrderItem, DeliveryTracking
)


@admin.register(DeliveryCompany)
class DeliveryCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'contact_phone', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'contact_email', 'contact_phone')
    list_editable = ('is_active',)  # Allow quick approval from list view
    actions = ['approve_companies', 'reject_companies']

    def approve_companies(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} company(ies) approved successfully.")

    approve_companies.short_description = "Approve selected companies"

    def reject_companies(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} company(ies) rejected.")

    reject_companies.short_description = "Reject selected companies"


@admin.register(DeliveryPerson)
class DeliveryPersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'company', 'delivery_type', 'is_available', 'rating')
    list_filter = ('delivery_type', 'is_available', 'company')
    search_fields = ('full_name', 'phone')


@admin.register(DeliveryOption)
class DeliveryOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_fee', 'estimated_time', 'is_active')
    list_editable = ('is_active', 'base_fee')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user__username', 'delivery_address')
    readonly_fields = ('order_number', 'subtotal', 'delivery_fee', 'total')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price_at_purchase')
    search_fields = ('order__order_number', 'product__name')


@admin.register(DeliveryTracking)
class DeliveryTrackingAdmin(admin.ModelAdmin):
    list_display = ('order', 'current_status', 'current_location', 'last_updated')
    list_filter = ('current_status',)
    search_fields = ('order__order_number',)
