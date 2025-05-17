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
    return render(request, 'bai2/cart.html', {'cart_items': cart_items, 'total_price': total_price})

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

def checkout(request):
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        shipping_name = request.POST.get('shipping_name')
        shipping_address = request.POST.get('shipping_address')
        shipping_phone = request.POST.get('shipping_phone')

        request.session['cart'] = {}

        return render(request, 'bai2/checkout_success.html', {
            'payment_method': payment_method,
            'shipping_name': shipping_name,
            'shipping_address': shipping_address,
            'shipping_phone': shipping_phone,
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
