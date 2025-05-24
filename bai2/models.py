from django.db import models
from django.contrib.auth.models import User

class Book(models.Model):

    CATEGORY_CHOICES = [
        ('van_hoc', 'Văn học'),
        ('giao_khoa', 'Giáo khoa'),
        ('ky_nang', 'Kỹ năng'),
        ('thieu_nhi', 'Thiếu nhi'),
        ('cong_nghe', 'Công nghệ'),
        ('ngoai_ngu', 'Ngoại ngữ'),
        ('tu_lieu', 'Tư liệu'),
        ('khac', 'Khác'),
    ]
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=20, decimal_places=0)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='van_hoc')
    cover_image = models.ImageField(upload_to='book_covers/', blank=True)
    available = models.BooleanField(default=True)
    pages = models.PositiveIntegerField(null=True, blank=True, verbose_name="Số trang")
    weight = models.PositiveIntegerField(null=True, blank=True, verbose_name="Trọng lượng (g)")
    release_date = models.DateField(null=True, blank=True, verbose_name="Ngày xuất bản")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=20, decimal_places=0)
    payment_method = models.CharField(max_length=50)
    shipping_name = models.CharField(max_length=100)
    shipping_address = models.TextField()
    shipping_phone = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default='Pending')

    def __str__(self):
        return f"Order {self.id} by {self.user.username} on {self.order_date.strftime('%Y-%m-%d')}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=20, decimal_places=0)

    def __str__(self):
        return f"{self.quantity} x {self.book.title}"

