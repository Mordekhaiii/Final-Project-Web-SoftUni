# Generated by Django 5.1.3 on 2024-12-13 14:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orders', '0002_product_description_product_is_available_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='Quantity')),
                ('total_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Total Price')),
                ('payment_method', models.CharField(choices=[('Cash', 'Cash'), ('QRIS', 'QRIS')], default='Cash', max_length=20, verbose_name='Payment Method')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Payment Date')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='orders.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_payments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Payments',
                'ordering': ['-date'],
            },
        ),
    ]
