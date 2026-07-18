from django.db import models
from django.contrib.auth.models import User
from dashboard.models import Product

class DeliveryCompany(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='delivery_companies/', blank=True, null=True)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField()
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class DeliveryPerson(models.Model):
    DELIVERY_TYPES = [
        ('bike', 'Bike/Motorcycle'),
        ('car', 'Car'),
        ('van', 'Van/Cargo'),
        ('matatu', 'Matatu/Public Transport'),
        ('ai_transport', 'AI/Specialized Transport (Perishables)'),
        ('pickup', 'Pickup Point'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='delivery_person')
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    company = models.ForeignKey(DeliveryCompany, on_delete=models.SET_NULL, null=True, blank=True, related_name='delivery_persons')
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_TYPES, default='bike')
    vehicle_number = models.CharField(max_length=50, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_deliveries = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    profile_picture = models.ImageField(upload_to='delivery_persons/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.get_delivery_type_display()})"


class DeliveryOption(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    base_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estimated_time = models.CharField(max_length=50, help_text="e.g. 30-60 mins")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_METHODS = [
        ('mpesa', 'M-Pesa'),
        ('card', 'Credit/Debit Card'),
        ('cash', 'Cash on Delivery'),
        ('bank', 'Bank Transfer'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    delivery_option = models.ForeignKey(DeliveryOption, on_delete=models.PROTECT)
    delivery_person = models.ForeignKey(DeliveryPerson, on_delete=models.SET_NULL, null=True, blank=True)
    
    delivery_address = models.TextField()
    delivery_notes = models.TextField(blank=True)
    
    # NEW FIELDS - Important for Map Tracking
    delivery_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Shop Location (SmartSME Ambassador)
    shop_latitude = models.DecimalField(max_digits=9, decimal_places=6, default=-1.2855, null=True, blank=True)
    shop_longitude = models.DecimalField(max_digits=9, decimal_places=6, default=36.8261, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.order_number} - {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            last_order = Order.objects.order_by('id').last()
            if last_order:
                self.order_number = f"ORD{str(last_order.id + 1).zfill(6)}"
            else:
                self.order_number = "ORD000001"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.price_at_purchase * self.quantity


class DeliveryTracking(models.Model):
    """Real-time delivery tracking"""
    STATUS_CHOICES = [
        ('assigned', 'Assigned to Delivery Person'),
        ('picked_up', 'Picked Up from Seller'),
        ('in_transit', 'In Transit'),
        ('near_destination', 'Near Destination'),
        ('delivered', 'Delivered'),
    ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='tracking')
    current_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    current_location = models.CharField(max_length=255, blank=True)
    estimated_arrival = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Tracking for Order #{self.order.order_number}"