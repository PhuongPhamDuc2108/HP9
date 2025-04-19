from django.shortcuts import render, get_object_or_404, redirect
from .models import Book

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
