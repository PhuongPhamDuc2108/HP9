from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'price', 'available')
    list_filter = ('available', 'created_at','author')
    search_fields = ('title', 'author')
    ordering = ('title',)

