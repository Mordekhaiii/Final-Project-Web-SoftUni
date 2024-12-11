from unicodedata import name
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('',views.home,name='home'),
    path('home.html',views.home,name='home'),
    path('login/', views.loginPage, name='login'),
    path('register',views.registerPage,name='register'),
    path('profile/', views.profilePage, name='profile'),
    path('logout/', views.logoutUser, name='logout'),
    path('profile/edit/', views.edit_user_profile, name='edit_profile'),
    path('contact/', views.contact, name='contact'),
    path('profile/update_profile', views.update_user_profile, name='update_profile'),
    path('cart/', views.view_cart, name='view_cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
]