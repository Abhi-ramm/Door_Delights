# Generated by Django 5.1.7 on 2025-04-10 14:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Customer', '0010_chatmessage_is_read_alter_chatmessage_sender'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessage',
            name='checkout',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Customer.checkout'),
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='sender',
            field=models.CharField(choices=[('customer', 'Customer'), ('chef', 'Chef')], max_length=10),
        ),
    ]
