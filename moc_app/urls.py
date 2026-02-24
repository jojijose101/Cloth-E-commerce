from django.urls import path

from moc_app import views
app_name = 'moc_app'
urlpatterns = [
    path('', views.index,name='index'),
    path('/<slug:c_slug>/<slug:p_slug>/',views.product,name='product'),
    path('/<slug:c_slug>/', views.index, name='product_of_cat'),



]