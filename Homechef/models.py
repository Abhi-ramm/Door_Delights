from django.db import models

class HomeChef_registration(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    id = models.AutoField(primary_key=True)
    photo = models.ImageField(upload_to='homechef_photos/')
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=10, unique=True)
    email = models.EmailField(unique=True)
    aadhaar_number = models.CharField(max_length=12, unique=True)
    dish = models.TextField()
    password = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.full_name} - {self.status}"
    
from django.db import models
from .models import HomeChef_registration

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Breakfast', 'Breakfast'),
        ('Lunch', 'Lunch'),
        ('Evening Snack', 'Evening Snack'),
        ('Dinner', 'Dinner'),
    ]

    chef = models.ForeignKey(HomeChef_registration, on_delete=models.CASCADE)  # Linked to HomeChef
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    supercoins = models.PositiveIntegerField(default=0)  # SuperCoins field
    stock = models.PositiveIntegerField(default=0)  # Stock field
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Breakfast')  # Category field
    image = models.ImageField(upload_to='product_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.name} by {self.chef.full_name} - {self.category} - Stock: {self.stock}"
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum([review.rating for review in reviews]) / len(reviews)
        return 0