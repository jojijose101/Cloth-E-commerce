from decimal import Decimal

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from cart_app.models import Cart, CartItem, Order, OrderItem
from moc_app.models import Product
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_http_methods
import razorpay

# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart
def add_cart(request,pr_id):
    product = Product.objects.get(id=pr_id)
    size = (request.POST.get('size') or '').strip()
    color = (request.POST.get('color') or '').strip()
    try:
        cart = Cart.objects.get(cartId=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cartId = _cart_id(request)
        )
        cart.save()
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, size=size, color=color)
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
        cart_item.save()


    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product = product,
            cart = cart,
            quantity = 1,
            size=size,
            color=color,

        )
        cart_item.save()
    return redirect('cart_app:cartdetails')


def _get_cart_items_and_total(request):
    total = Decimal('0.00')
    counter = 0
    cart = Cart.objects.get(cartId=_cart_id(request))
    cart_items = CartItem.objects.filter(cart=cart, active=True)
    for item in cart_items:
        total += (Decimal(item.product.price) * item.quantity)
        counter += item.quantity
    return cart, cart_items, total, counter

def cart_details(request):
    total = Decimal("0.00")
    counter = 0
    cart_items = CartItem.objects.none() 

    try:
        cart, cart_items, total, counter = _get_cart_items_and_total(request)
    except ObjectDoesNotExist:
        pass

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "total": total,
        "counter": counter,
    })

def cart_remove(request, item_id):
    cart = Cart.objects.get(cartId=_cart_id(request))
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart_app:cartdetails')

def deletion(request, item_id):
    cart = Cart.objects.get(cartId=_cart_id(request))
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()
    return redirect('cart_app:cartdetails')


@require_http_methods(["GET", "POST"])
@login_required
def checkout(request):
    try:
        cart, cart_items, total, counter = _get_cart_items_and_total(request)
    except Exception:
        messages.info(request, "Your cart is empty.")
        return redirect("cart_app:cartdetails")

    if not cart_items.exists():
        messages.info(request, "Your cart is empty.")
        return redirect("cart_app:cartdetails")

    gateway_enabled = bool(getattr(settings, "RAZORPAY_KEY_ID", "") and getattr(settings, "RAZORPAY_KEY_SECRET", ""))

    form_data = {
        "full_name": "",
        "phone": "",
        "email": request.user.email or "",
        "address": "",
        "payment_method": "online",
    }

    order = None
    razorpay_order_id = None
    razorpay_amount = None
    razorpay_currency = "INR"

    if request.method == "POST":
        form_data["full_name"] = (request.POST.get("full_name") or "").strip()
        form_data["phone"] = (request.POST.get("phone") or "").strip()
        form_data["email"] = (request.POST.get("email") or "").strip()
        form_data["address"] = (request.POST.get("address") or "").strip()
        form_data["payment_method"] = (request.POST.get("payment_method") or "online").strip()

        if not form_data["full_name"] or not form_data["phone"] or not form_data["address"]:
            return render(request, "checkout.html", {
                "cart_items": cart_items, "total": total, "counter": counter,
                "gateway_enabled": gateway_enabled, "error": "Please fill all required fields.",
                "form_data": form_data,
            })

        # ✅ Create order
        order = Order.objects.create(
            user=request.user,
            full_name=form_data["full_name"],
            phone=form_data["phone"],
            email=form_data["email"],
            address=form_data["address"],
            total_amount=total,
            currency="INR",
            payment_method=form_data["payment_method"],
            is_paid=False,
            status="placed" if form_data["payment_method"] == "cod" else "payment_pending",
        )

        # ✅ Create order items
        for ci in cart_items:
            OrderItem.objects.create(
                order=order,
                product=ci.product,
                quantity=ci.quantity,
                price=Decimal(ci.product.price),
                size=ci.size,
                color=ci.color,
            )

        # ✅ COD: finish now
        if form_data["payment_method"] == "cod":
            CartItem.objects.filter(cart=cart).delete()
            messages.success(request, "Order placed successfully (Cash on Delivery).")
            return redirect("moc_app:my_orders")

        # ✅ ONLINE: create Razorpay order
        if not gateway_enabled:
            order.status = "payment_failed"
            order.save(update_fields=["status"])
            return render(request, "checkout.html", {
                "cart_items": cart_items, "total": total, "counter": counter,
                "gateway_enabled": gateway_enabled, "error": "Payment gateway not configured.",
                "form_data": form_data,
            })

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_amount = int(Decimal(total) * 100)

        rp_order = client.order.create({
            "amount": razorpay_amount,
            "currency": "INR",
            "payment_capture": 1
        })

        razorpay_order_id = rp_order["id"]
        order.razorpay_order_id = razorpay_order_id
        order.save(update_fields=["razorpay_order_id"])

        return render(request, "checkout.html", {
            "cart_items": cart_items,
            "total": total,
            "counter": counter,
            "gateway_enabled": gateway_enabled,
            "order": order,
            "razorpay_order_id": razorpay_order_id,
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
            "razorpay_amount": razorpay_amount,
            "razorpay_currency": razorpay_currency,
            "form_data": form_data,  # ✅ preserves inputs
        })

    return render(request, "checkout.html", {
        "cart_items": cart_items,
        "total": total,
        "counter": counter,
        "gateway_enabled": gateway_enabled,
        "form_data": form_data,
    })


@require_http_methods(["POST"])
@login_required
def verify_payment(request):
    """Verify Razorpay signature, mark paid, and clear cart."""
    rp_payment_id = request.POST.get('razorpay_payment_id', '')
    rp_order_id = request.POST.get('razorpay_order_id', '')
    rp_signature = request.POST.get('razorpay_signature', '')

    order = Order.objects.filter(razorpay_order_id=rp_order_id).first()
    if not order:
        return render(request, 'payment_failed.html', {'message': 'Order not found.'})

    razorpay_key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
    razorpay_key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '')
    if not (razorpay_key_id and razorpay_key_secret):
        order.status = 'failed'
        order.save(update_fields=['status'])
        return render(request, 'payment_failed.html', {'message': 'Payment gateway not configured.'})

    try:
        import razorpay
        client = razorpay.Client(auth=(razorpay_key_id, razorpay_key_secret))
        client.utility.verify_payment_signature({
            'razorpay_order_id': rp_order_id,
            'razorpay_payment_id': rp_payment_id,
            'razorpay_signature': rp_signature,
        })
    except Exception as e:
        order.status = 'failed'
        order.save(update_fields=['status'])
        return render(request, 'payment_failed.html', {'message': f'Payment verification failed: {e}'})

    order.status = "placed"
    order.is_paid = True
    order.payment_method = "online"
    order.razorpay_payment_id = rp_payment_id
    order.razorpay_signature = rp_signature
    order.save(update_fields=["status", "is_paid", "payment_method", "razorpay_payment_id", "razorpay_signature"])

    # Clear cart after successful payment
    try:
        cart = Cart.objects.get(cartId=_cart_id(request))
        CartItem.objects.filter(cart=cart).delete()
    except Exception:
        pass

    return render(request, 'payment_success.html', {'order': order})