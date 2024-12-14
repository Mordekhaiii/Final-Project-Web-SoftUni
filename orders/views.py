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
    try:
        # Use filter to handle multiple orders
        order = Order.objects.filter(user=request.user).first()  # or use .order_by('-created_at').first() for the most recent order

        if order:
            return render(request, 'orders/product_list.html', {'order': order})
        else:
            # Handle case where no order is found
            return render(request, 'orders/no_order.html')
    except Exception as e:
        return render(request, 'orders/error.html', {'error': str(e)})

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



# Cekout
from .models import Order, OrderItem, Product
from .forms import OrderForm, OrderItemForm
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt


from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json


@login_required
@require_http_methods(["POST"])
def checkout(request):
    try:
        # Parse the JSON data from the request body
        data = json.loads(request.body)

        # Extract checkout details
        total = data.get('total')
        items = data.get('items')

        # Validate the data
        if not total or not items:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid checkout data'
            }, status=400)

        # Create an order
        order = Order.objects.create(
            user=request.user,
            total_price=total,
            status='pending'
        )

        # Create order items
        for item in items:
            OrderItem.objects.create(
                order=order,
                product_id=item['id'],
                quantity=item['quantity'],
                price=item['price']
            )

        # Return success response with order ID
        return JsonResponse({
            'status': 'success',
            'order_id': order.id,
            'message': 'Order placed successfully!'
        })

    except Exception as e:
        # Log the error
        print(f"Checkout error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'An unexpected error occurred'
        }, status=500)


@login_required
def payment_order(request, order_id):
    # Retrieve the specific order
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Get order items
    order_items = order.item_set.all()

    return render(request, 'orders/payment.html', {
        'order': order,
        'order_items': order_items
    })

@login_required
def create_order(request):
    if request.method == 'POST':
        try:
            # Parse the cart data from the request
            cart_data = json.loads(request.body)

            # Create a new order
            order = Order.objects.create(
                user=request.user,
                total_price=cart_data.get('total', 0),
                status='pending'
            )

            # Create order items
            for item in cart_data.get('items', []):
                product = Product.objects.get(id=item['id'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price=item['price']
                )

            # Clear the cart or perform any additional processing
            return JsonResponse({
                'status': 'success',
                'order_id': order.id,
                'message': 'Order created successfully'
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)





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

# Product Checkout
from django.views.decorators.http import require_http_methods
@login_required
@require_http_methods(["POST"])
def product_checkout(request):
    try:
        # Parse the JSON data from the request body
        data = json.loads(request.body)
        # Extract checkout details
        total = data.get('total')
        items = data.get('items')

        # Validate the data
        if not total or not items:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid checkout data'
            }, status=400)

        # Create an order
        order = Order.objects.create(
            user=request.user,
            total_price=total,
            status='pending'
        )

        # Create order items
        for item in items:
            OrderItem.objects.create(
                order=order,
                product_id=item['id'],
                quantity=item['quantity'],
                price=item['price']
            )

        # Return success response with order ID
        return JsonResponse({
            'status': 'success',
            'order_id': order.id,
            'redirect_url': f'/orders/checkout/{order.id}/'
        })

    except Exception as e:
        # Log the error
        print(f"Checkout error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'An unexpected error occurred'
        }, status=500)


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


# def product_list(request):
#     products = Product.objects.all()  # Fetch all products from the database
#     return render(request, 'halaman/product_list.html', {'products': products})

