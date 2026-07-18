from django.contrib import admin
from .models import MpesaTransaction


@admin.register(MpesaTransaction)
class MpesaTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'order', 
        'phone_number', 
        'amount', 
        'mpesa_receipt_number', 
        'status', 
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
        'mpesa_receipt_number',
        'result_code',
        'result_desc',
        'created_at',
        'updated_at'
    )