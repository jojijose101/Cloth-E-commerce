from django.urls import path
from . import views

app_name = 'cart_app'

urlpatterns = [

    path('/add/<int:pr_id>/', views.add_cart, name='addcart'),
    path('/cart', views.cart_details, name='cartdetails'),
    path('remove/<int:pro_id>/', views.cart_remove, name='cart_remove'),
    path('delete/<int:pr_id>/', views.deletion, name='cart_delete'),

]