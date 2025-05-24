from django.shortcuts import render, get_object_or_404, redirect
from .models import Book
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm

def book_list(request):
    category = request.GET.get('category')
    books = Book.objects.filter(available=True)
    if category:
        books = books.filter(category=category)
    context = {
        'books': books,
        'category_choices': Book.CATEGORY_CHOICES,
        'selected_category': category,
    }
    return render(request, 'bai2/book_list.html', context)

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk, available=True)
    return render(request, 'bai2/book_detail.html', {'book': book})

def add_to_cart(request, book_id):
    book = get_object_or_404(Book, pk=book_id, available=True)
    cart = request.session.get('cart', {})
    if str(book_id) in cart:
        cart[str(book_id)] += 1
    else:
        cart[str(book_id)] = 1
    request.session['cart'] = cart
    return redirect('bai2:view_cart')

def update_cart_item(request, book_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        if quantity > 0:
            cart[str(book_id)] = quantity
        else:
            if str(book_id) in cart:
                del cart[str(book_id)]
        request.session['cart'] = cart
    return redirect('bai2:view_cart')

def remove_cart_item(request, book_id):
    cart = request.session.get('cart', {})
    if str(book_id) in cart:
        del cart[str(book_id)]
    request.session['cart'] = cart
    return redirect('bai2:view_cart')

def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    for book_id, quantity in cart.items():
        book = get_object_or_404(Book, pk=book_id)
        item_total = book.price * quantity
        total_price += item_total
        cart_items.append({
            'book': book,
            'quantity': quantity,
            'item_total': item_total,
        })

    discount = 0
    applied_voucher = None

    if request.method == 'POST':
        voucher_code = request.POST.get('voucher_code', '').strip().upper()
        vouchers = {
            'SALE10': 0.10,
            'BUY2GET1': 0,  # Special handling needed, skip for now
            'FREESHIP': 0,  # Shipping not handled here, skip
        }
        if voucher_code in vouchers:
            if voucher_code == 'SALE10' and total_price > 500000:
                discount = total_price * vouchers[voucher_code]
                applied_voucher = voucher_code
            else:
                # For simplicity, only implement SALE10 discount here
                applied_voucher = None
        else:
            applied_voucher = None

        request.session['applied_voucher'] = applied_voucher
        request.session['discount'] = discount

    else:
        applied_voucher = request.session.get('applied_voucher')
        discount = request.session.get('discount', 0)

    final_price = total_price - discount

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'discount': discount,
        'final_price': final_price,
        'applied_voucher': applied_voucher,
    }
    return render(request, 'bai2/cart.html', context)

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from .models import Order, OrderItem
from django.contrib.auth.decorators import login_required

@login_required
def checkout(request):
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        shipping_name = request.POST.get('shipping_name')
        shipping_address = request.POST.get('shipping_address')
        shipping_phone = request.POST.get('shipping_phone')

        cart = request.session.get('cart', {})
        if not cart:
            messages.error(request, "Giỏ hàng trống.")
            return redirect('bai2:book_list')

        total_price = 0
        for book_id, quantity in cart.items():
            book = get_object_or_404(Book, pk=book_id)
            total_price += book.price * quantity

        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            payment_method=payment_method,
            shipping_name=shipping_name,
            shipping_address=shipping_address,
            shipping_phone=shipping_phone,
            status='Pending',
        )

        for book_id, quantity in cart.items():
            book = get_object_or_404(Book, pk=book_id)
            OrderItem.objects.create(
                order=order,
                book=book,
                quantity=quantity,
                price=book.price,
            )

        request.session['cart'] = {}

        return render(request, 'bai2/checkout_success.html', {
            'payment_method': payment_method,
            'shipping_name': shipping_name,
            'shipping_address': shipping_address,
            'shipping_phone': shipping_phone,
            'order': order,
        })
    else:
        return render(request, 'bai2/checkout.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect('bai2:book_list')
        else:
            messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'bai2/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful.")
            return redirect('bai2:book_list')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'bai2/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('bai2:book_list')

from django.contrib.auth.decorators import login_required

@login_required
def order_history(request):
    orders = request.user.orders.all().order_by('-order_date')
    return render(request, 'bai2/order_history.html', {'orders': orders})

def promotions_view(request):
    vouchers = [
        {
            'title': 'Giảm 10% cho đơn hàng trên 500K',
            'code': 'SALE10',
            'description': 'Áp dụng cho tất cả các sản phẩm trong giỏ hàng.',
            'valid_until': '31/12/2024',
        },
        {
            'title': 'Mua 2 tặng 1',
            'code': 'BUY2GET1',
            'description': 'Áp dụng cho sách văn học và kỹ năng.',
            'valid_until': '30/11/2024',
        },
        {
            'title': 'Miễn phí vận chuyển cho đơn hàng trên 300K',
            'code': 'FREESHIP',
            'description': 'Áp dụng cho tất cả các đơn hàng.',
            'valid_until': '31/12/2024',
        },
    ]
    return render(request, 'bai2/promotions.html', {'vouchers': vouchers})
