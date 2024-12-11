import profile

from django.shortcuts import render,HttpResponse, redirect
from django.contrib.auth.forms import UserCreationForm
from halaman.forms import CreateUserForm
import logging
from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.models import User


from .models import Order, OrderItem, Product
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

@login_required
def checkout_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            total = data.get('total')
            items = data.get('items')

            if not items or total is None:
                return JsonResponse({'status': 'error', 'message': 'Invalid cart data'}, status=400)

            # Create the order
            order = Order.objects.create(
                user=request.user,
                total_price=total,
                status='Pending'
            )

            for item in items:
                product_id = item.get('id')
                quantity = item.get('quantity')

                try:
                    product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': f'Product with id {product_id} does not exist'}, status=404)

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )

            # Return URL for redirection
            return JsonResponse({'status': 'success', 'redirect_url': f'/orders/payment/process/{order.id}/'})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# Payment
@login_required
def payment_view(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        return render(request, 'orders/order_payment.html', {'order': order})
    except Order.DoesNotExist:
        return redirect('order_list')  # Redirect to orders if the order is not found


# Process Payment
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Order

def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # Logika lainnya, misalnya memproses pembayaran
    return render(request, 'orders/payment.html', {'order': order})
# Payment End
# Process Payment End


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
# Order Detail End

@login_required
def user_orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')  # Fetch orders for the logged-in user
    return render(request, 'orders/orders.html', {'orders': orders})

def product_list_view(request):
    products = Product.objects.all()
    return render(request, 'orders/product_list.html', {'products': products})
# Checkout End

# Order
from django.shortcuts import render, get_object_or_404
from orders.models import Order


@login_required
def order_payment_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.status == 'Paid':
        return redirect('order_detail', order_id=order.id)

    # Handle payment logic here, for example, integrating with a payment gateway
    if request.method == 'POST':
        # Simulating payment success
        order.status = 'Paid'
        order.save()
        return redirect('order_detail', order_id=order.id)

    return render(request, 'orders/order_payment.html', {'order': order})

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

# Payment
def payment(request):
    # Fetch cart items and total from session or database
    cart_items = request.session.get('cart_items', [])
    cart_total = sum(item['total'] for item in cart_items)

    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'order_reference': 'REF123456',  # Example order reference
    }
    return render(request, 'orders/payment.html', context)

def confirm_payment(request):
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        # Process payment logic here
        return redirect('order_history')



# Cekout
# from django.http import JsonResponse
# from .models import Order
#
# def checkout(request):
#     if request.method == 'POST':
#         try:
#             # Ambil data dari request
#             data = json.loads(request.body)
#             total = data.get('total')
#             items = data.get('items')
#
#             # Buat pesanan (contoh sederhana)
#             order = Order.objects.create(user=request.user, total=total)
#
#             # Simpan item pesanan jika diperlukan
#             for item in items:
#                 order.items.create(
#                     product_id=item['id'],
#                     quantity=item['quantity'],
#                     price=item['price']
#                 )
#
#             # Return respons JSON dengan order_id
#             return JsonResponse({
#                 'status': 'success',
#                 'order_id': order.id
#             })
#         except Exception as e:
#             return JsonResponse({'status': 'error', 'message': str(e)})
#     return JsonResponse({'status': 'error', 'message': 'Invalid request method'})