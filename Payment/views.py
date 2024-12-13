from django.shortcuts import render, get_object_or_404, redirect
from .models import Payment, Product
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from django.db import transaction
from .forms import PaymentForm  # Impor PaymentForm
from .models import Product, Payment
from orders.models import Order


@login_required
def delete_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    try:
        with transaction.atomic():

            product = payment.product
            product.stock += payment.quantity
            product.is_available = True
            product.save()

            payment.delete()

    except Exception as e:
        pass

    return redirect('payment_list')


@login_required
def decrease_quantity(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    try:
        with transaction.atomic():
            if payment.quantity > 1:
                payment.quantity -= 1
                payment.total_price = payment.quantity * payment.product.price
                payment.save()

                perfume = payment.product
                perfume.stock += 1
                perfume.is_available = True
                perfume.save()

    except Exception as e:
        pass

    return redirect('payment_list')


@login_required

def payment_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Hitung total harga jika belum ada
    if not order.total_price:
        total_price = sum(item.price * item.quantity for item in order.items.all())
        order.total_price = total_price
        order.save()

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

        # Proses pembayaran
        order.payment_method = payment_method
        order.payment_status = 'Paid'
        order.status = 'Completed'
        order.save()

        messages.success(request, 'Your payment was successful!')
        return redirect('user_orders')

    return render(request, 'payment/payment_order.html', {'order': order})