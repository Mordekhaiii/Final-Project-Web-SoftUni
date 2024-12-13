from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from Payment.models import Payment
from django.contrib.auth.decorators import login_required
from orders.models import Product
from django.db import transaction
from django.http import HttpResponseBadRequest

from .models import Order, OrderItem, Product
from django.http import JsonResponse
import json

from django.urls import reverse

#Admin Only Product
from .forms import ProductForm

def is_admin(user):
    return user.is_staff

from django.contrib.auth.decorators import login_required, user_passes_test


# Untuk Liat Views Product List Ketika Login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Order, OrderItem

@login_required
def product_list(request):
    # Get or create the order for the logged-in user (only unpaid orders)
    order, created = Order.objects.get_or_create(user=request.user, paid_amount__isnull=True)

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = Product.objects.get(id=product_id)

        # Add product to the user's order
        order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

        # Update product stock
        if product.stock > 0:
            product.stock -= 1
            product.save()
        else:
            # If out of stock, show message (optional)
            return redirect('product_list')  # Redirect back if out of stock

        # Redirect to payment page
        return redirect('payment_order')

    # Fetch all products
    products = Product.objects.all()

    context = {
        'products': products,
        'order': order,  # Send the order to the template
    }
    return render(request, 'orders/product_list_crud.html', context)

# Ketika tidak Login
def product_list_view(request):
    products = Product.objects.all()
    return render(request, 'orders/product_list_crud.html', {'products': products})

def product_setting(request):
    # Handle form submission
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_setting')
    else:
        form = ProductForm()

    # Get all products
    products = Product.objects.all()

    # Create a list of products with their stock values directly from the Product model
    products_with_stock = []
    for product in products:
        # Get stock from the Product model
        stock = product.stock  # Get the stock value from the model directly
        products_with_stock.append({'product': product, 'stock': stock})

    # Pass both form and product information to the template
    return render(request, 'orders/product_setting.html', {'form': form, 'products_with_stock': products_with_stock})


# Update Stock Product Admin
@user_passes_test(is_admin)
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Produk berhasil ditambahkan!")
            return redirect('product_list')
        else:
            messages.error(request, "Gagal menambahkan produk. Periksa form.")
    else:
        form = ProductForm()
    return render(request, 'orders/product_form.html', {'form': form})

def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')  # Redirect ke daftar produk setelah berhasil menambah
    else:
        form = ProductForm()
    return render(request, 'orders/product_add.html', {'form': form})

def product_edit(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')  # Redirect ke daftar produk setelah berhasil mengedit
    else:
        form = ProductForm(instance=product)
    return render(request, 'orders/product_edit.html', {'form': form, 'product': product})



# Admin Update Stock
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from .models import Product

@user_passes_test(is_admin)
def update_stock(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        if 'increase' in request.POST:
            product.stock += 1  # Increase stock by 1
        elif 'decrease' in request.POST:
            if product.stock > 0:
                product.stock -= 1  # Decrease stock by 1 if stock is greater than 0
            else:
                error_message = "Stock cannot be negative."
                return render(request, 'orders/update_stock.html', {'product': product, 'error_message': error_message})

        product.save()
        return HttpResponseRedirect(reverse('product_summary', args=[product.pk]))  # Redirect back to product summary page

    return render(request, 'orders/update_stock.html', {'product': product})
# Stock
# Admin Delete Product
@user_passes_test(is_admin)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Produk berhasil dihapus.")
        return redirect('product_list')
    return render(request, 'orders/product_confirm_delete.html', {'product': product})


# Checkout
@login_required
def checkout(request):
    if request.method == 'POST':
        # Simpan data pesanan
        user = request.user
        items = request.session.get('cart', {})  # Ambil data dari session (contoh keranjang belanja)
        if not items:
            messages.error(request, 'Your cart is empty.')
            return redirect('cart')

        order = Order.objects.create(user=user, status='Pending')
        total_price = 0

        for product_id, quantity in items.items():
            product = get_object_or_404(Product, id=product_id)
            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price,
            )
            total_price += product.price * quantity

            # Update stok produk
            product.stock -= quantity
            product.save()

        order.total_price = total_price
        order.save()

        # Hapus keranjang setelah checkout
        del request.session['cart']

        messages.success(request, 'Your order has been placed successfully.')
        return redirect('order_history')

    return render(request, 'orders/checkout.html')
# Checkout




# Order Detail
from django.shortcuts import render, get_object_or_404
from .models import Order


@login_required
def order_detail(request, order_id):
    try:
        # Ambil detail pesanan berdasarkan ID
        order = Order.objects.get(id=order_id, user=request.user)
        order_items = OrderItem.objects.filter(order=order)

        # Kirim data ke template untuk ditampilkan
        return render(request, 'orders/order_detail.html', {
            'order': order,
            'order_items': order_items,
        })
    except Order.DoesNotExist:
        return render(request, '404.html', {'message': 'Order not found'}, status=404)

def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_detail.html', {'order': order})


# Alur dari payment_order ke user_order_views
@login_required
def user_orders_view(request):
    # Ambil semua pesanan user yang sedang login, diurutkan dari yang terbaru
    orders = Order.objects.filter(user=request.user, paid_amount__isnull=False).order_by('-created_at')

    # Hitung total harga setiap pesanan jika perlu
    for order in orders:
        # Menggunakan related_name 'order_items'
        total_price = sum(item.product.price * item.quantity for item in order.items.all())
        order.total_price = total_price
        order.save()

    # data untuk template
    context = {
        'orders': orders
    }
    return render(request, 'orders/orders.html', context)


# Alur End


def product_checkout(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
        # Proses checkout atau logic lainnya
        return render(request, "orders/checkout.html", {"product": product, "quantity": quantity})

    return render(request, "orders/checkout.html", {"product": product})

# Order List
@login_required
def order_list_view(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_list.html', {'orders': orders})
# Order List End

# Home Start
def home(request):
    try:
        order = get_object_or_404(Order, user=request.user)  # Adjust as necessary
        print(f"Order ID: {order.id}")  # Debugging line
    except Exception as e:
        print(f"Error: {e}")  # Print any errors
        order = None  # Set order to None if there's an error
    return render(request, 'home.html', {'order': order})


# Home End


from django.db.models import Q

def product_summary(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'orders/product_summary.html', {'product': product})


