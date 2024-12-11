from django.contrib import admin
from .models import UserProfile
from .models import Order



admin.site.register(UserProfile)


# Cekout Admin
from .models import Product, Cart, CartItem, Order
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1

class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]

admin.site.register(Product)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order)