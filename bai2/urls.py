from django.urls import path
from . import views

app_name = 'bai2'

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path('add-to-cart/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('update-cart-item/<int:book_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove-cart-item/<int:book_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('promotions/', views.promotions_view, name='promotions'),
    path('order-history/', views.order_history, name='order_history'),
    path('apply-coupon/<int:coupon_id>/', views.apply_coupon, name='apply_coupon'),
    path('stores/', views.stores_view, name='stores'),
]
