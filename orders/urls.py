from django.urls import path
from . import views
from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home.html',views.home,name='home'),
    path('', views.user_orders_view, name='user_orders'),
    path('products/', views.product_list_view, name='product_list'),  # Display the products
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/<int:order_id>/', views.payment_view, name='payment'),
    path('payment/process/<int:order_id>/', views.process_payment, name='process_payment'),
    path('list/', views.order_list_view, name='order_list'),
    path('detail/<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('payment/', views.payment, name='payment'),
    path('confirm_payment/', views.confirm_payment, name='confirm_payment'),
    path('orders/payment/process/<int:order_id>/', views.process_payment, name='process_payment'),
    path('orders/details/<int:order_id>/', views.order_detail, name='order_detail'),

]