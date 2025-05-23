# Generated by Django 5.1.7 on 2025-03-27 08:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Customer', '0005_alter_checkout_status'),
        ('Delivery_Boys', '0005_deliveryassignment'),
        ('Homechef', '0004_product_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='Complaint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('homechef', 'Home Chef'), ('delivery', 'Delivery')], max_length=10)),
                ('complaint_text', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('resolved', 'Resolved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Customer.customer')),
                ('delivery_boy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Delivery_Boys.deliveryboy')),
                ('home_chef', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Homechef.homechef_registration')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Customer.checkout')),
            ],
        ),
    ]
