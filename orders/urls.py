from django.urls import path
from . import views
from django.urls import path, include
from django.contrib import admin
from .views import product_list, product_create, product_update, product_delete
from .views import product_list

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home.html',views.home,name='home'),
    path('', views.user_orders_view, name='user_orders'),
    path('products/', views.product_list, name='product_list'),  # Display the products
    # Admin
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/update/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('product/add/', views.product_add, name='product_add'),
    path('product/<int:id>/edit/', views.product_edit, name='product_edit'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('product/<int:id>/payment/', views.payment_view, name='payment'),
    # End
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
