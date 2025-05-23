# Generated by Django 5.1.7 on 2025-03-24 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Customer', '0004_remove_checkout_cart_orderitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkout',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('on the way', 'On the way'), ('cancelled', 'Cancelled')], default='pending', max_length=10),
        ),
    ]
