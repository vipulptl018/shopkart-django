from django.urls import path
from . import views
from .views import add_cart
urlpatterns = [
    path('', views.cart, name='cart'),
    path('add_cart/<int:product_id>/', views.add_cart, name='add_cart'),
    path('cart_quantity_remove/<int:product_id>/<int:cart_item_id>/',views.cart_quantity_remove, name='cart_quantity_remove'),
    path('remove_cart_items/<int:product_id>/<int:cart_item_id>/', views.remove_cart_items, name='remove_cart_items'),
]
