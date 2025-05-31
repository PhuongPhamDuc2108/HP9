from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Coupon, Order, OrderItem
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.utils import timezone
from decimal import Decimal

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
    applied_coupon = None

    if request.method == 'POST':
        coupon_code = request.POST.get('voucher_code', '').strip().upper()
        try:
            coupon = Coupon.objects.get(
                code=coupon_code,
                active=True,
                valid_from__lte = timezone.now(),
                valid_until__gte =timezone.now()
            )

            # Check if the order meets the minimum value requirement
            if total_price >= coupon.min_order_value:
                if coupon.discount_type == 'percentage':
                    discount = total_price * (coupon.discount_value / 100)
                else:  # fixed amount
                    discount = coupon.discount_value

                applied_coupon = coupon
                messages.success(request, f"Mã giảm giá {coupon.code} đã được áp dụng.")
            else:
                messages.error(request, f"Đơn hàng cần đạt tối thiểu {coupon.min_order_value} VNĐ để áp dụng mã này.")
                applied_coupon = None
        except Coupon.DoesNotExist:
            messages.error(request, "Mã giảm giá không hợp lệ hoặc đã hết hạn.")
            applied_coupon = None

        request.session['applied_coupon_id'] = applied_coupon.id if applied_coupon else None
        request.session['discount'] = float(discount)

    else:
        coupon_id = request.session.get('applied_coupon_id')
        if coupon_id:
            try:
                applied_coupon = Coupon.objects.get(id=coupon_id)
            except Coupon.DoesNotExist:
                applied_coupon = None
                request.session['applied_coupon_id'] = None

        discount = Decimal(request.session.get('discount', 0))

    final_price = total_price - discount

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'discount': discount,
        'final_price': final_price,
        'applied_coupon': applied_coupon,
    }
    return render(request, 'bai2/cart.html', context)

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from .models import Order, OrderItem
from django.contrib.auth.decorators import login_required

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Giỏ hàng trống.")
        return redirect('bai2:book_list')

    # Calculate cart totals
    total_price = 0
    cart_items = []
    for book_id, quantity in cart.items():
        book = get_object_or_404(Book, pk=book_id)
        item_total = book.price * quantity
        total_price += item_total
        cart_items.append({
            'book': book,
            'quantity': quantity,
            'item_total': item_total,
        })

    # Get applied coupon and discount
    coupon = None
    discount = 0
    coupon_id = request.session.get('applied_coupon_id')
    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            discount = Decimal(request.session.get('discount', 0))
        except Coupon.DoesNotExist:
            pass

    final_price = total_price - discount

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        shipping_name = request.POST.get('shipping_name')
        shipping_address = request.POST.get('shipping_address')
        shipping_phone = request.POST.get('shipping_phone')

        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            coupon=coupon,
            discount=discount,
            final_price=final_price,
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

        # Clear cart and coupon data
        request.session['cart'] = {}
        request.session['applied_coupon_id'] = None
        request.session['discount'] = 0

        return render(request, 'bai2/checkout_success.html', {
            'payment_method': payment_method,
            'shipping_name': shipping_name,
            'shipping_address': shipping_address,
            'shipping_phone': shipping_phone,
            'order': order,
        })
    else:
        context = {
            'cart_items': cart_items,
            'total_price': total_price,
            'discount': discount,
            'final_price': final_price,
            'coupon': coupon,
        }
        return render(request, 'bai2/checkout.html', context)

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
    # Get all active coupons
    coupons = Coupon.objects.filter(
        active=True,
        valid_from__lte=timezone.now(),
        valid_until__gte=timezone.now()
    )

    # If there are no coupons in the database, create some default ones
    if not coupons.exists():
        # Create default coupons if none exist
        default_coupons = [
            {
                'code': 'SALE10',
                'title': 'Giảm 10% cho đơn hàng trên 500K',
                'description': 'Áp dụng cho tất cả các sản phẩm trong giỏ hàng.',
                'discount_type': 'percentage',
                'discount_value': 10,
                'min_order_value': 500000,
                'valid_until': timezone.now() + timezone.timedelta(days=365),
            },
            {
                'code': 'SALE20',
                'title': 'Giảm 20% cho đơn hàng trên 1 triệu',
                'description': 'Áp dụng cho tất cả các sản phẩm trong giỏ hàng.',
                'discount_type': 'percentage',
                'discount_value': 20,
                'min_order_value': 1000000,
                'valid_until': timezone.now() + timezone.timedelta(days=180),
            },
            {
                'code': 'FIXED100K',
                'title': 'Giảm 100K cho đơn hàng trên 800K',
                'description': 'Áp dụng cho tất cả các đơn hàng.',
                'discount_type': 'fixed',
                'discount_value': 100000,
                'min_order_value': 800000,
                'valid_until': timezone.now() + timezone.timedelta(days=90),
            },
        ]

        for coupon_data in default_coupons:
            Coupon.objects.create(
                code=coupon_data['code'],
                title=coupon_data['title'],
                description=coupon_data['description'],
                discount_type=coupon_data['discount_type'],
                discount_value=coupon_data['discount_value'],
                min_order_value=coupon_data['min_order_value'],
                valid_from=timezone.now(),
                valid_until=coupon_data['valid_until'],
                active=True
            )

        # Refresh the coupons queryset
        coupons = Coupon.objects.filter(
            active=True,
            valid_from__lte=timezone.now(),
            valid_until__gte=timezone.now()
        )

    return render(request, 'bai2/promotions.html', {'coupons': coupons})

def apply_coupon(request, coupon_id):
    # Check if user has items in cart
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Giỏ hàng trống. Vui lòng thêm sản phẩm trước khi áp dụng mã giảm giá.")
        return redirect('bai2:book_list')

    # Calculate cart total
    total_price = 0
    for book_id, quantity in cart.items():
        book = get_object_or_404(Book, pk=book_id)
        total_price += book.price * quantity

    try:
        coupon = Coupon.objects.get(
            id=coupon_id,
            active=True,
            valid_from__lte=timezone.now(),
            valid_until__gte=timezone.now()
        )

        # Check if the order meets the minimum value requirement
        if total_price >= coupon.min_order_value:
            if coupon.discount_type == 'percentage':
                discount = total_price * (coupon.discount_value / 100)
            else:  # fixed amount
                discount = coupon.discount_value

            request.session['applied_coupon_id'] = coupon.id
            request.session['discount'] = float(discount)

            messages.success(request, f"Mã giảm giá {coupon.code} đã được áp dụng. Bạn tiết kiệm được {int(discount):,} ₫.")
        else:
            messages.error(request, f"Đơn hàng cần đạt tối thiểu {coupon.min_order_value:,} ₫ để áp dụng mã này.")

    except Coupon.DoesNotExist:
        messages.error(request, "Mã giảm giá không hợp lệ hoặc đã hết hạn.")

    return redirect('bai2:view_cart')
