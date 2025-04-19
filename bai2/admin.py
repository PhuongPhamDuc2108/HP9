from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'price', 'available', 'pages', 'weight', 'release_date', 'category')
    list_filter = ('available', 'created_at', 'author', 'category')
    search_fields = ('title', 'author')
    ordering = ('title',)
    fields = ('title', 'author', 'price', 'description', 'cover_image', 'available', 'pages', 'weight', 'release_date', 'category')
