from django.contrib import admin
from django.urls import path

from halaman import views
from payments.views import checkout_view, product_view, check_payment_info_view
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', product_view, name='index'),
    path('checkout/<product_id>', checkout_view, name='checkout'),
    path('payment-confirmation/<reference_id>', check_payment_info_view, name='payment-confirmation'),

]
