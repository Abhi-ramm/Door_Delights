from django.db import models

# Create your models here.
from django.db import models

class DeliveryBoy(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    AVAILABILITY_STATUS_CHOICES = [
        ('available', 'Available'),
        ('not_available', 'Not Available'),
    ]
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    aadhaar_number = models.CharField(max_length=12, unique=True)
    license_number = models.CharField(max_length=20, unique=True)
    photo = models.ImageField(upload_to='delivery_boy_photos/')
    password = models.CharField(max_length=255)  # Consider hashing passwords before storing
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    availability_status = models.CharField(max_length=15, choices=AVAILABILITY_STATUS_CHOICES, default='not_available')


    def __str__(self):
        return f"{self.full_name} ({self.get_status_display()} - {self.get_availability_status_display()})"
    
from Customer.models import Checkout
from Delivery_Boys.models import DeliveryBoy
class DeliveryAssignment(models.Model):
    order = models.ForeignKey(Checkout, on_delete=models.CASCADE)  # The order assigned
    delivery_boy = models.ForeignKey(DeliveryBoy, on_delete=models.CASCADE)  # Delivery boy who is assigned to the order
    assigned_at = models.DateTimeField(auto_now_add=True)  # Timestamp for assignment
    status = models.CharField(max_length=20, choices=[
        ('assigned', 'Assigned'),
        ('delivering', 'Delivering'),
        ('delivered', 'Delivered'),
    ], default='assigned')  # Status of the assignment

    def __str__(self):
        return f"Order #{self.order.id} assigned to {self.delivery_boy.name}"

   