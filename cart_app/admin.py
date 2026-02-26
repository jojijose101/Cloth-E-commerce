from django.contrib import admin

from .models import Cart, CartItem, Order, OrderItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('cartId', 'date_added')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'size', 'color', 'active')
    list_filter = ('active', 'size', 'color')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone', 'total_amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('id', 'full_name', 'phone', 'razorpay_order_id', 'razorpay_payment_id')
    inlines = [OrderItemInline]
