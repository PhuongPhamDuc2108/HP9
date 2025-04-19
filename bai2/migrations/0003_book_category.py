# Generated by Django 4.2.20 on 2025-04-19 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bai2', '0002_book_pages_book_release_date_book_weight'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='category',
            field=models.CharField(choices=[('van_hoc', 'Văn học'), ('giao_khoa', 'Giáo khoa'), ('ky_nang', 'Kỹ năng'), ('thieu_nhi', 'Thiếu nhi'), ('cong_nghe', 'Công nghệ'), ('ngoai_ngu', 'Ngoại ngữ')], default='van_hoc', max_length=20),
        ),
    ]
