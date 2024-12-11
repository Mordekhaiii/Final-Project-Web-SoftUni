import profile

from django.shortcuts import render,HttpResponse, redirect
from django.contrib.auth.forms import UserCreationForm
from halaman.forms import CreateUserForm
import logging
from .models import UserProfile
from .forms import EditProfileForm
from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.models import User

# Checkout Start
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Checkout End


@login_required
def home(request):
    return render(request, 'home.html', {
        'user': request.user,
    })


logger = logging.getLogger(__name__)
# Create your views here.
def home(request):
    logger.info("Home view accessed")
    return render(request, 'home.html')

# Update Profile
from .forms import UserUpdateForm, CustomPasswordChangeForm
from django.contrib.auth.forms import PasswordChangeForm

@login_required
def update_user_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)

        if user_form.is_valid() and password_form.is_valid():
            # Simpan perubahan username dan email
            user_form.save()
            # Simpan perubahan password
            password_form.save()
            # Perbarui sesi pengguna
            update_session_auth_hash(request, password_form.user)

            messages.success(request, 'Profil berhasil diperbarui!')
            return redirect('update_profile')
        else:
            messages.error(request, 'Terjadi kesalahan. Silakan periksa form Anda.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        password_form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'accounts/change_password.html', {
        'user_form': user_form,
        'password_form': password_form,
    })

# Timestap setiap file
from django.utils.timezone import now

def contact_view(request):
    return render(request, 'contact.html', {'timestamp': now().timestamp()})

def home_view(request):
    return render(request, 'home.html', {'timestamp': now().timestamp()})


def registerPage(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {form.cleaned_data["username"]}')

            return redirect('login')

    context = {'form' :form}
    return render(request, 'accounts/register.html', context)

def loginPage(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username or password incorrect')

    context = {}
    return render(request, 'accounts/login.html', context)

def profilePage(request):
    if not request.user.is_authenticated:
        messages.info(request, "You need to log in to view your profile.")
        return redirect('login')

    # Ambil profil pengguna yang sedang login (dari UserProfile)
    profile = UserProfile.objects.filter(user=request.user).first()

    context = {
        'user': request.user,
        'profile': profile  # Tambahkan profil pengguna ke context
    }
    return render(request, 'accounts/profile.html', context)

def logoutUser(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('home')


@login_required
def profile_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username or password incorrect')

    context = {}
    return render(request, 'home.html', context)

@login_required
def profile_view(request):
    user_profile = UserProfile.objects.get(user=request.user)
    return render(request, 'accounts/profile.html', {'user_profile': user_profile})


@login_required
def profilePage(request):
    if not request.user.is_authenticated:
        messages.info(request, "You need to log in to view your profile.")
        return redirect('login')

    # Ambil profil pengguna yang sedang login
    profile = UserProfile.objects.filter(user=request.user).first()

    # Jika nama kosong, tampilkan 'Unknown'
    first_name = request.user.first_name if request.user.first_name else "Unknown"
    last_name = request.user.last_name if request.user.last_name else ""

    context = {
        'user': request.user,
        'profile': profile,
        'full_name': f"{first_name} {last_name}".strip(),  # Gabungkan nama depan dan belakang
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_user_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        user_profile.user.first_name = request.POST.get("name")
        user_profile.phone_number = request.POST.get("phone_number")
        user_profile.address = request.POST.get("address")
        user_profile.age = request.POST.get("age")

        if 'profile_picture' in request.FILES:
            user_profile.profile_picture = request.FILES['profile_picture']

        user_profile.user.save()
        user_profile.save()

        return redirect('profile')  # Ganti 'profile' dengan nama URL untuk halaman profil

    return render(request, 'accounts/edit_profile.html', {'user_profile': user_profile})

def contact(request):
    return render(request, 'contact.html')


# Views Cekout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Product, Cart, CartItem, Order


@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    total_price = sum(item.total_price for item in cart.items.all())
    return render(request, 'home.html', {'cart': cart, 'total_price': total_price})


@login_required
def add_to_cart(request, product_id):
    cart, created = Cart.objects.get_or_create(user=request.user)
    product = Product.objects.get(id=product_id)

    # Check if the product is already in the cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:  # If the item already exists in the cart, update the quantity
        cart_item.quantity += 1
    cart_item.save()

    return JsonResponse({'status': 'success', 'message': 'Item added to cart'})


@login_required
def remove_from_cart(request, product_id):
    cart = Cart.objects.get(user=request.user)
    cart_item = CartItem.objects.get(cart=cart, product__id=product_id)
    cart_item.delete()

    return JsonResponse({'status': 'success', 'message': 'Item removed from cart'})


@login_required
def checkout(request):
    cart = Cart.objects.get(user=request.user)
    total_price = sum(item.total_price for item in cart.items.all())

    # Create an order from the cart
    order = Order.objects.create(cart=cart, user=request.user, total_price=total_price)

    # Optionally clear the cart after checkout
    cart.items.all().delete()

    return redirect('order_detail', order_id=order.id)


def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'order_detail.html', {'order': order})

