from django.shortcuts import render, get_object_or_404, redirect
from .models import Payment, Product
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from django.db import transaction
from .forms import PaymentForm  # Impor PaymentForm
from .models import Product, Payment
from orders.models import Order, OrderItem


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
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Hitung total harga jika belum ada
    if not order.total_price:
        total_price = sum(item.price * item.quantity for item in order.items.all())
        order.total_price = total_price
        order.save()
        print(f"Total Price: {order.total_price}")  # Debugging output

    if request.method == 'POST':
        # Jika request adalah POST, proses order dan pembayaran
        if 'add_product' in request.POST:
            # Tambah produk ke pesanan
            product_id = request.POST.get('product_id')
            quantity = int(request.POST.get('quantity', 1))

            product = get_object_or_404(Product, id=product_id)

            if product.stock < quantity:
                messages.error(request, "Stok tidak mencukupi untuk produk ini.")
                return redirect('payment_order', order_id=order_id)

            # Tambah atau perbarui item di dalam pesanan
            order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
            if not created:
                order_item.quantity += quantity
            else:
                order_item.quantity = quantity

            order_item.price = product.price
            order_item.save()

            # Kurangi stok produk
            product.stock -= quantity
            product.save()

            # Hitung ulang total harga pesanan
            order.total_price = sum(item.price * item.quantity for item in order.items.all())
            order.save()

            messages.success(request, f"Produk {product.name} berhasil ditambahkan ke pesanan.")
            return redirect('payment_order', order_id=order_id)

        elif 'payment_method' in request.POST:
            # Proses pembayaran
            payment_method = request.POST.get('payment_method')
            order.payment_method = payment_method
            order.payment_status = 'Paid'
            order.status = 'Completed'
            order.save()

            messages.success(request, 'Pembayaran berhasil diproses!')
            return redirect('user_orders')

    # Ambil semua produk untuk ditampilkan di halaman pembayaran
    products = Product.objects.filter(stock__gt=0)

    return render(request, 'payment/payment_order.html', {
        'order': order,
        'products': products
    })