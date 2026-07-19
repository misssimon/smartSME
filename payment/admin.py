from django.contrib import admin
from .models import MpesaTransaction
from django.utils.html import format_html


@admin.register(MpesaTransaction)
class MpesaTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'order_link',
        'phone_number', 
        'amount', 
        'mpesa_receipt_number', 
        'status',           # ← Real field for editing
        'created_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = (
        'order__order_number', 
        'phone_number', 
        'mpesa_receipt_number'
    )
    readonly_fields = (
        'checkout_request_id', 
        'merchant_request_id',
        'result_code',
        'result_desc',
        'created_at',
        'updated_at'
    )
    list_editable = ('status',)   # Now works correctly
    
    actions = ['approve_selected_payments', 'mark_as_failed']

    def order_link(self, obj):
        return format_html('<a href="{}">{}</a>', 
            f"/admin/checkout/order/{obj.order.id}/change/", 
            obj.order.order_number
        )
    order_link.short_description = 'Order'

    def approve_selected_payments(self, request, queryset):
        updated = 0
        for transaction in queryset:
            if transaction.status != 'approved':
                transaction.status = 'approved'
                transaction.save()
                
                order = transaction.order
                order.status = 'confirmed'
                order.save()
                updated += 1

        self.message_user(request, f"{updated} payment(s) approved and orders set to confirmed.")
    
    approve_selected_payments.short_description = "Approve selected payments"

    def mark_as_failed(self, request, queryset):
        queryset.update(status='failed')
        self.message_user(request, f"{queryset.count()} payment(s) marked as failed.")
    
    mark_as_failed.short_description = "Mark selected as Failed"