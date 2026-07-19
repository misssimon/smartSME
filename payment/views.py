from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
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
MPESA_CALLBACK_URL = 'https://smartsme.onrender.com/payment/mpesa-callback/'


# ==================== EMAIL HELPERS ====================

def send_order_status_email(order, subject, template_name):
    """Send email to customer"""
    try:
        html_message = render_to_string(f'checkout/email/{template_name}', {   # Fixed path
            'order': order,
            'user': order.user,
            'site_name': 'smartSME',
        })
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.user.email],
        )
        email.content_subtype = 'html'
        email.send(fail_silently=True)
        print(f"✅ Email sent to customer: {order.user.email}")
    except Exception as e:
        print(f"⚠️ Customer email failed: {e}")


def send_admin_notification(order, message):
    """Send immediate notification to admin"""
    try:
        admin_email = 'soshisunny073@gmail.com'
        html_message = render_to_string('checkout/email/admin_payment_notification.html', {  # Fixed path
            'order': order,
            'message': message,
        })
        email = EmailMessage(
            subject=f"New M-Pesa Payment Request - Order #{order.order_number}",
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[admin_email],
        )
        email.content_subtype = 'html'
        email.send(fail_silently=True)
        print(f"✅ Admin notified for Order #{order.order_number}")
    except Exception as e:
        print(f"⚠️ Admin notification failed: {e}")


# ==================== MPESA CORE FUNCTIONS ====================

def get_mpesa_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    try:
        response = requests.get(url, auth=(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET), timeout=10)
        response.raise_for_status()
        return response.json().get('access_token')
    except Exception as e:
        print(f"Token error: {e}")
        return None


def initiate_mpesa_stk_push(order, phone_number):
    access_token = get_mpesa_access_token()
    if not access_token:
        return {"ResponseCode": "1", "errorMessage": "Failed to get access token"}

    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode((MPESA_SHORTCODE + MPESA_PASSKEY + timestamp).encode()).decode('utf-8')

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

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        return response.json()
    except Exception as e:
        return {"ResponseCode": "1", "errorMessage": str(e)}


# ==================== VIEWS ====================

@login_required
def mpesa_payment(request, order_number):
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

            # === Send notification to admin immediately ===
            send_admin_notification(order, "New M-Pesa Payment Request (STK Push Initiated)")

            messages.success(request, "Payment request sent successfully! Check your phone for M-Pesa prompt.")
            return redirect('payment:mpesa_request_sent', order_number=order.order_number)
        else:
            messages.error(request, f"Payment request failed: {response.get('errorMessage')}")
            return redirect('checkout:my_orders')

    return render(request, 'payment/mpesa_payment.html', {'order': order})


@login_required
def mpesa_request_sent(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'payment/mpesa_request_sent.html', {'order': order})


# ==================== MANUAL APPROVAL BY ADMIN ====================

@login_required
def approve_payment(request, transaction_id):
    """Manual approval by admin"""
    transaction = get_object_or_404(MpesaTransaction, id=transaction_id)
    order = transaction.order

    if request.method == 'POST':
        transaction.status = 'approved'
        transaction.mpesa_receipt_number = request.POST.get('receipt_number', 'MANUAL_APPROVED')
        transaction.save()

        order.status = 'confirmed'
        order.save()

        send_order_status_email(order, f"Payment Approved - Order #{order.order_number}", 'order_confirmed.html')
        send_admin_notification(order, "Payment Manually Approved by Admin")

        messages.success(request, f"Payment for Order #{order.order_number} has been approved.")
        return redirect('admin:payment_mpesatransaction_changelist')

    return render(request, 'payment/admin_approve_payment.html', {
        'transaction': transaction,
        'order': order
    })


# ==================== MPESA CALLBACK ====================

def mpesa_callback(request):
    import json
    try:
        data = json.loads(request.body)
        stk_callback = data.get('Body', {}).get('stkCallback', {})

        checkout_request_id = stk_callback.get('CheckoutRequestID')
        result_code = stk_callback.get('ResultCode')

        transaction = MpesaTransaction.objects.get(checkout_request_id=checkout_request_id)
        transaction.result_code = result_code
        transaction.result_desc = stk_callback.get('ResultDesc', '')
        transaction.status = 'success' if result_code == 0 else 'failed'

        if result_code == 0:
            for item in stk_callback.get('CallbackMetadata', {}).get('Item', []):
                if item.get('Name') == 'MpesaReceiptNumber':
                    transaction.mpesa_receipt_number = item.get('Value')

            order = transaction.order
            order.status = 'confirmed'
            order.save()

            send_order_status_email(order, f"Payment Successful - Order #{order.order_number}", 'order_confirmed.html')
            send_admin_notification(order, "M-Pesa Payment Successful")

        transaction.save()

    except Exception as e:
        print(f"M-Pesa Callback Error: {e}")

    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})


# Card Payment (Placeholder)
@login_required
def card_payment(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'payment/card_payment.html', {'order': order})