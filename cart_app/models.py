

from django.db import models
from django.contrib.auth.models import User

from moc_app.models import Product


# Create your models here.

class Cart(models.Model):
    cartId = models.CharField(max_length=250,blank=True)
    date_added = models.DateTimeField(auto_now_add =True)

    class Meta:
        db_table = 'Cart'
        ordering = ['date_added']
    def __str__(self):
        return '{}'.format(self.cartId)


class CartItem(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE)
    quantity = models.IntegerField()
    # Clothing selections
    size = models.CharField(max_length=20, blank=True)
    color = models.CharField(max_length=30, blank=True)
    active = models.BooleanField(default=True)
    class Meta:
        db_table = 'CartItem'
    def sub_total(self):
        return self.product.price * self.quantity
    def __str__(self):
        return '{}'.format(self.product)


class Order(models.Model):
    PAYMENT_CHOICES = (
        ("online", "Online (Razorpay)"),
        ("cod", "Cash on Delivery"),
    )

    STATUS_CHOICES = (
        ("placed", "Placed"),
        ("packed", "Packed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),

        ("payment_pending", "Payment Pending"),
        ("payment_failed", "Payment Failed"),

        # ✅ Keep old statuses so old records don't break (safe)
        ("created", "Created (Old)"),
        ("paid", "Paid (Old)"),
        ("failed", "Failed (Old)"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    full_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30)
    address = models.TextField()

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="INR")

    # ✅ NEW
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default="online")
    is_paid = models.BooleanField(default=False)

    # Razorpay
    razorpay_order_id = models.CharField(max_length=120, blank=True)
    razorpay_payment_id = models.CharField(max_length=120, blank=True)
    razorpay_signature = models.CharField(max_length=255, blank=True)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="placed")

    def __str__(self):
        return f"Order #{self.id} ({self.payment_method}, {self.status})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=20, blank=True)
    color = models.CharField(max_length=30, blank=True)

    def line_total(self):
        return self.price * self.quantity
