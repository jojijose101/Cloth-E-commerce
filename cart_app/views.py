from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404

from cart_app.models import Cart, CartItem
from moc_app.models import Product
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart
def add_cart(request,pr_id):
    product = Product.objects.get(id=pr_id)
    try:
        cart = Cart.objects.get(cartId=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cartId = _cart_id(request)
        )
        cart.save()
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
        cart_item.save()


    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product = product,
            cart = cart,
            quantity = 1

        )
        cart_item.save()
    return redirect('cart_app:cartdetails')

def cart_details(request,total=0,counter=0,cart_item=None):
    try:
        cart = Cart.objects.get(cartId = _cart_id(request))

        cart_items = CartItem.objects.filter(cart=cart,active=True)
        print(cart_items)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            counter += cart_item.quantity
    except ObjectDoesNotExist:
        pass
    return render(request,'cart.html',dict(cart_items=cart_items,total=total,counter=counter,))

def cart_remove(request,pro_id):
    cart = Cart.objects.get(cartId=_cart_id(request))
    product = get_object_or_404(Product,id=pro_id)
    cart_item = CartItem.objects.get(product=product,cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart_app:cartdetails')

def deletion(request,pr_id):
    cart = Cart.objects.get(cartId=_cart_id(request))
    product = get_object_or_404(Product, id=pr_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart_app:cartdetails')