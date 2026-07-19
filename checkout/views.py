from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal
from dashboard.models import Cart
from .models import (
    Order, OrderItem, DeliveryOption, DeliveryPerson, 
    DeliveryCompany, DeliveryTracking
)
from .forms import CompanyRegistrationForm


# ==================== EMAIL HELPERS ====================

def send_order_status_email(order, subject, template_name):
    """Reusable function to send order status emails"""
    try:
        html_message = render_to_string(f'checkout/email/{template_name}', {
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
        print(f"✅ Status email sent to {order.user.email} - {subject}")
    except Exception as e:
        print(f"⚠️ Failed to send status email: {e}")


def send_admin_notification(order, message):
    """Send notification to admin"""
    try:
        admin_email = 'soshisunny073@gmail.com'
        html_message = render_to_string('checkout/email/admin_order_notification.html', {
            'order': order,
            'message': message,
        })
        email = EmailMessage(
            subject=f"Order Update - #{order.order_number}",
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[admin_email],
        )
        email.content_subtype = 'html'
        email.send(fail_silently=True)
        print(f"✅ Admin notified for Order #{order.order_number}")
    except Exception as e:
        print(f"⚠️ Admin notification failed: {e}")


# ==================== CHECKOUT ====================

@login_required
def checkout(request):
    try:
        cart = request.user.cart
    except:
        messages.warning(request, "Your cart is empty.")
        return redirect('dashboard:buyer_dashboard')

    if cart.total_items == 0:
        messages.warning(request, "Your cart is empty.")
        return redirect('dashboard:buyer_dashboard')

    delivery_options = DeliveryOption.objects.filter(is_active=True)

    context = {
        'cart': cart,
        'delivery_options': delivery_options,
    }
    return render(request, 'checkout/checkout.html', context)


@login_required
@transaction.atomic
def place_order(request):
    if request.method != 'POST':
        return redirect('checkout:checkout')

    try:
        cart = request.user.cart
    except:
        messages.error(request, "Cart not found.")
        return redirect('dashboard:buyer_dashboard')

    if cart.total_items == 0:
        messages.error(request, "Your cart is empty.")
        return redirect('dashboard:buyer_dashboard')

    payment_method = request.POST.get('payment_method')
    delivery_option_id = request.POST.get('delivery_option')
    delivery_address = request.POST.get('delivery_address')
    delivery_notes = request.POST.get('delivery_notes', '')
    delivery_latitude = request.POST.get('delivery_latitude')
    delivery_longitude = request.POST.get('delivery_longitude')

    if not all([payment_method, delivery_option_id, delivery_address]):
        messages.error(request, "Please fill all required fields.")
        return redirect('checkout:checkout')

    delivery_option = get_object_or_404(DeliveryOption, id=delivery_option_id)

    subtotal = cart.total_price
    delivery_fee = delivery_option.base_fee
    if 'pickup' in delivery_option.name.lower():
        delivery_fee = Decimal('0.00')

    total = subtotal + delivery_fee

    order = Order.objects.create(
        user=request.user,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        total=total,
        payment_method=payment_method,
        delivery_option=delivery_option,
        delivery_address=delivery_address.strip(),
        delivery_notes=delivery_notes,
        delivery_latitude=delivery_latitude if delivery_latitude else None,
        delivery_longitude=delivery_longitude if delivery_longitude else None,
        shop_latitude=-1.2855,
        shop_longitude=36.8261,
        status='pending'
    )

    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price_at_purchase=item.product.discounted_price
        )

    cart.items.all().delete()
    DeliveryTracking.objects.create(order=order)

    # Send Order Placed Email
    send_order_status_email(order, f"Order Placed Successfully - #{order.order_number}", 'order_placed.html')
    send_admin_notification(order, "New Order Placed")

    messages.success(request, f"Order #{order.order_number} placed successfully!")
    return redirect('checkout:order_success', order_number=order.order_number)


@login_required
def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'checkout/order_success.html', {'order': order})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'checkout/my_orders.html', {'orders': orders})


@login_required
def track_order(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    try:
        tracking = order.tracking
    except DeliveryTracking.DoesNotExist:
        tracking = None

    context = {
        'order': order,
        'tracking': tracking,
    }
    return render(request, 'checkout/track_order.html', context)


# ==================== COMPANY REGISTRATION ====================

def company_registration(request):
    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save()
            
            # Send confirmation to company
            try:
                html_message = render_to_string('checkout/email/company_registration.html', {'company': company})
                email = EmailMessage(
                    subject=f'Application Received - {company.name}',
                    body=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[company.contact_email],
                )
                email.content_subtype = 'html'
                email.send(fail_silently=True)
            except Exception as e:
                print(f"Company email failed: {e}")

            messages.success(request, f"Thank you! Your company '{company.name}' has been registered.")
            return redirect('checkout:company_registration_success')
    else:
        form = CompanyRegistrationForm()

    return render(request, 'checkout/company_registration.html', {'form': form})


def company_registration_success(request):
    return render(request, 'checkout/company_registration_success.html')