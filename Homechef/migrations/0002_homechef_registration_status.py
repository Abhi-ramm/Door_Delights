# Generated by Django 5.1.7 on 2025-03-22 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Homechef', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='homechef_registration',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending', max_length=10),
        ),
    ]
