from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal
import requests
import base64
from datetime import datetime
from checkout.models import Order
from .models import MpesaTransaction


# ==================== DARAJA API CONFIG ====================
MPESA_CONSUMER_KEY = '8hYi846dzPSqBKAC3ZbEqkkJzOQFx95xnQLqIg6b2sL2thb0'
MPESA_CONSUMER_SECRET = 'STITyxyFUIXAnCIVrRRueWnKV5wk3rZsfhxozk5wQzhoCwSAvBYLsPukttzvsPBh'
MPESA_SHORTCODE = '5515738'
MPESA_PASSKEY = '4cbd2d6babc8827c7ab0a433c7ec754b7b945a7a71aca5277db0a024f160b462'
MPESA_CALLBACK_URL = 'https://smartsme.onrender.comS/payment/mpesa-callback/'


def get_mpesa_access_token():
    """Get OAuth token from Daraja"""
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    
    try:
        response = requests.get(url, auth=(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET), timeout=10)
        response.raise_for_status()  # Raise error for bad status codes
        return response.json().get('access_token')
    except Exception as e:
        print(f"Error getting M-Pesa token: {e}")
        return None


def initiate_mpesa_stk_push(order, phone_number):
    """Initiate M-Pesa STK Push"""
    access_token = get_mpesa_access_token()
    
    if not access_token:
        return {"ResponseCode": "1", "errorMessage": "Failed to get access token from Daraja"}

    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(
        (MPESA_SHORTCODE + MPESA_PASSKEY + timestamp).encode()
    ).decode('utf-8')

    payload = {
        "BusinessShortCode": MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(order.total),
        "PartyA": phone_number,
        "PartyB": MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": MPESA_CALLBACK_URL,
        "AccountReference": order.order_number,
        "TransactionDesc": f"Payment for Order {order.order_number}"
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        return response.json()
    except Exception as e:
        return {"ResponseCode": "1", "errorMessage": str(e)}


@login_required
def mpesa_payment(request, order_number):
    """M-Pesa payment page"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    if request.method == 'POST':
        phone = request.POST.get('phone_number')

        if not phone.startswith('254'):
            phone = '254' + phone.lstrip('0')

        transaction = MpesaTransaction.objects.create(
            order=order,
            phone_number=phone,
            amount=order.total,
            status='pending'
        )

        response = initiate_mpesa_stk_push(order, phone)

        if response.get('ResponseCode') == '0':
            transaction.checkout_request_id = response.get('CheckoutRequestID')
            transaction.merchant_request_id = response.get('MerchantRequestID')
            transaction.save()

            return redirect('payment:mpesa_request_sent', order_number=order.order_number)
        else:
            error_msg = response.get('errorMessage', 'Unknown error occurred')
            messages.error(request, f"Payment request failed: {error_msg}")
            return redirect('checkout:my_orders')

    context = {
        'order': order,
    }
    return render(request, 'payment/mpesa_payment.html', context)


@login_required
def mpesa_request_sent(request, order_number):
    """Confirmation page after STK Push is sent"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'payment/mpesa_request_sent.html', {'order': order})


@login_required
def mpesa_callback(request):
    """Handle M-Pesa Callback from Safaricom"""
    import json

    try:
        data = json.loads(request.body)
        stk_callback = data.get('Body', {}).get('stkCallback', {})

        checkout_request_id = stk_callback.get('CheckoutRequestID')
        result_code = stk_callback.get('ResultCode')
        result_desc = stk_callback.get('ResultDesc')

        transaction = MpesaTransaction.objects.get(checkout_request_id=checkout_request_id)
        transaction.result_code = result_code
        transaction.result_desc = result_desc
        transaction.status = 'success' if result_code == 0 else 'failed'

        if result_code == 0:
            callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
            for item in callback_metadata:
                if item.get('Name') == 'MpesaReceiptNumber':
                    transaction.mpesa_receipt_number = item.get('Value')

            order = transaction.order
            order.status = 'confirmed'
            order.save()

        transaction.save()

    except Exception as e:
        print(f"M-Pesa Callback Error: {str(e)}")

    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})


@login_required
def card_payment(request, order_number):
    """Credit/Debit Card payment page (placeholder)"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'payment/card_payment.html', {'order': order})