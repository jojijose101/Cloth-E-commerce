from django.urls import path

from moc_app import views
app_name = 'moc_app'
urlpatterns = [
    path('', views.index,name='index'),
    path("my-orders/", views.my_orders, name="my_orders"),
    path("my-orders/<int:order_id>/", views.order_detail, name="order_detail"),
    path('<slug:c_slug>/<slug:p_slug>/',views.product,name='product'),
    path('<slug:c_slug>/', views.index, name='product_of_cat'),



]