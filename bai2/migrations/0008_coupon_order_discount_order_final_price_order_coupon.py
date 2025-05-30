# Generated by Django 4.2.21 on 2025-05-31 05:36

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bai2', '0007_order_orderitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, unique=True)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('discount_type', models.CharField(choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Amount')], max_length=10)),
                ('discount_value', models.DecimalField(decimal_places=0, max_digits=10)),
                ('min_order_value', models.DecimalField(decimal_places=0, default=0, max_digits=10)),
                ('valid_from', models.DateTimeField(default=datetime.datetime(2025, 5, 31, 5, 36, 1, 781161, tzinfo=datetime.timezone.utc))),
                ('valid_until', models.DateTimeField()),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='discount',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=20),
        ),
        migrations.AddField(
            model_name='order',
            name='final_price',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=20),
        ),
        migrations.AddField(
            model_name='order',
            name='coupon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='bai2.coupon'),
        ),
    ]
