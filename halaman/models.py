from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, default="Default bio")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    name = models.CharField(max_length=255, default="Unknown")
    age = models.IntegerField(default=0)
    birth_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.user.username

# Model Cekout
from django.db import models
from django.contrib.auth.models import User

# Model for products
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    img = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return self.name

# Model for Cart
class Cart(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_checked_out = models.BooleanField(default=False)

    def __str__(self):
        return f"Cart {self.id} - {self.user}"

# Model for Cart Items (to store items in the cart)
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"

# Model for Order (when the cart is checked out)
class Order(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, null=True, blank=True)  # nullable sementara
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Pending')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    @property
    def cart_items(self):
        return self.cart.items.all()



