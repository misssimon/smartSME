from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


class FarmerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    farm_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='farmers/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.farm_name or self.user.username


class Product(models.Model):
    UNIT_CHOICES = [
        ('kg', 'Kilogram (kg)'),
        ('g', 'Gram (g)'),
        ('liter', 'Liter'),
        ('piece', 'Piece'),
        ('bunch', 'Bunch'),
        ('crate', 'Crate'),
        ('ton', 'Ton'),
    ]

    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='kg')
    quantity_in_stock = models.PositiveIntegerField(default=0)
    discount_percentage = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    expiry_date = models.DateField(null=True, blank=True)
    ideal_temperature = models.CharField(max_length=50, blank=True)
    specifications = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} by {self.farmer.username}"

    @property
    def discounted_price(self):
        if self.discount_percentage > 0:
            discount_factor = Decimal(1) - (Decimal(self.discount_percentage) /Decimal(100))
            return round(self.price_per_unit * discount_factor, 2)
        return self.price_per_unit

    @property
    def is_low_stock(self):
        return self.quantity_in_stock < 10


class ProductImage(models.Model):
    """Additional / sub images for products (varieties, details, etc.)"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/sub_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sub-image for {self.product.name}"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.product.discounted_price * self.quantity