from django.db import models
from checkout.models import Order


class MpesaTransaction(models.Model):
    """Store M-Pesa transaction records"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='mpesa_transactions')
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    checkout_request_id = models.CharField(max_length=100, blank=True, null=True)
    merchant_request_id = models.CharField(max_length=100, blank=True, null=True)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True, null=True)
    result_code = models.IntegerField(null=True, blank=True)
    result_desc = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='pending')  # pending, success, failed
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"M-Pesa Tx for Order #{self.order.order_number}"