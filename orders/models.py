from django.db import models
from django.contrib.auth.models import User
from products.models import Product, ProductVariant
from django.core.validators import MinValueValidator
import uuid
from django.utils import timezone
from decimal import Decimal


class Offer(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.code


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    offer = models.ForeignKey(Offer, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart {self.id}"
    
    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())
    
    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    def get_shipping_cost(self, shipping_state=None):
        """
        Calculate shipping cost based on state:
        - Giza and Cairo: LE 70
        - Any other state: LE 90
        """
        if shipping_state and shipping_state.lower() in ['giza', 'cairo']:
            return Decimal('70.00')
        return Decimal('90.00')
    
    def get_final_total(self, shipping_state=None):
        """Calculate final total including shipping"""
        subtotal = self.get_total_price()
        if self.offer and self.offer.is_active:
            subtotal -= (subtotal * self.offer.discount_percent / Decimal('100.00'))
        shipping = self.get_shipping_cost(shipping_state)
        total = subtotal + shipping
        return total.quantize(Decimal('0.01'))


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    customization_text = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['cart', 'product', 'variant', 'customization_text']
    
    def get_total_price(self):
        if self.variant:
            return self.variant.final_price * self.quantity
        return self.product.final_price * self.quantity
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=200, unique=True)
    email = models.EmailField(max_length=255)
    
    # Order details
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    offer = models.ForeignKey(Offer, null=True, blank=True, on_delete=models.SET_NULL)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Shipping information
    shipping_name = models.CharField(max_length=100)
    shipping_email = models.EmailField()
    shipping_phone = models.CharField(max_length=20, blank=True)
    shipping_address_line1 = models.CharField(max_length=200)
    shipping_address_line2 = models.CharField(max_length=200, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100)
    
    # Billing information (optional, can be same as shipping)
    billing_name = models.CharField(max_length=100, blank=True)
    billing_email = models.EmailField(blank=True)
    billing_phone = models.CharField(max_length=20, blank=True)
    billing_address_line1 = models.CharField(max_length=200, blank=True)
    billing_address_line2 = models.CharField(max_length=200, blank=True)
    billing_city = models.CharField(max_length=100, blank=True)
    billing_state = models.CharField(max_length=100, blank=True)
    billing_postal_code = models.CharField(max_length=20, blank=True)
    billing_country = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Additional fields
    notes = models.TextField(blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            self.order_number = f"ORD-{timestamp}-{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    customization_text = models.CharField(max_length=200, blank=True)
    
    # Store product details at time of purchase
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=100, blank=True)
    size_name = models.CharField(max_length=10, blank=True)
    color_name = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity} - Order {self.order.order_number}"


class ShippingMethod(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_days = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name


class OrderTracking(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking_updates')
    status = models.CharField(max_length=50)
    message = models.TextField()
    location = models.CharField(max_length=200, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.status}"