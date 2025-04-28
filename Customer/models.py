from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10, unique=True)
    address = models.TextField()
    password = models.CharField(max_length=255)  # Stored as plain text
    supercoins = models.IntegerField(default=0)  # Will be updated after orders

    def _str_(self):
        return self.name
    
class Cart(models.Model):
    user = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    def _str_(self):
        return f"Cart of {self.user.name}"  # Accessing the name of the related customer


from Homechef.models import Product

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)  # Cart linked to cart items
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Product linked to cart items
    quantity = models.PositiveIntegerField(default=1)  # Quantity of the product in the cart

    def _str_(self):
        return f"{self.quantity} x {self.product.name}"

    def get_total_price(self):
        """Calculate the total price for this cart item (product price * quantity)."""
        return self.product.price * self.quantity

    def get_total_supercoins(self):
        """Calculate the total SuperCoins required to purchase this cart item (product SuperCoins * quantity)."""
        return self.product.supercoins * self.quantity
    
class Checkout(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)  # User who placed order
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Total price
    supercoins_used = models.IntegerField(default=0)  # Applied SuperCoins
    amount_to_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Amount after discounts
    created_at = models.DateTimeField(auto_now_add=True)  # Order timestamp
    updated_at = models.DateTimeField(auto_now=True)  # Last update timestamp

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('on the way', 'On the way'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')

    PAYMENT_METHOD_CHOICES = [
        ('supercoins', 'Supercoins'),
        ('card', 'Card'),
        ('cash', 'Cash'),
    ]
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='supercoins')

    def _str_(self):
        return f"Order #{self.id} by {self.customer.username}"

    def create_order_items(self, cart):
        """Move cart items into OrderItem and clear the cart."""
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=self,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price_at_purchase=cart_item.product.price
            )
        cart.items.all().delete()  # Clear the cart after order creation

# ✅ OrderItem Model (Products inside an order)
class OrderItem(models.Model):
    order = models.ForeignKey(Checkout, on_delete=models.CASCADE, related_name="order_items")  # Links to an order
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # The product that was purchased
    quantity = models.PositiveIntegerField()  # Quantity ordered
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)  # Price at order time

    def _str_(self):
        return f"{self.quantity} x {self.product.name} (Order #{self.order.id})"
    
from django.db import models
from Customer.models import Customer, Checkout
from Delivery_Boys.models import DeliveryBoy
from Homechef.models import HomeChef_registration

class Complaint(models.Model):
    CATEGORY_CHOICES = [
        ('homechef', 'Home Chef'),
        ('delivery boy', 'Delivery Boy'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order = models.ForeignKey(Checkout, on_delete=models.CASCADE)
    home_chef = models.ForeignKey(HomeChef_registration, null=True, blank=True, on_delete=models.SET_NULL)
    delivery_boy = models.ForeignKey(DeliveryBoy, null=True, blank=True, on_delete=models.SET_NULL)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    complaint_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ], default='pending')

    def str(self):
        chef_name = self.home_chef.full_name if self.home_chef else "N/A"
        delivery_name = self.delivery_boy.full_name if self.delivery_boy else "N/A"
        category_name = "Home Chef" if self.category == "homechef" else "Delivery"
        
        return f"Complaint by {self.customer.name} - {category_name} - {chef_name if self.category == 'homechef' else delivery_name} ({self.status})"
    
class Review(models.Model):
    product = models.ForeignKey(Product, related_name="reviews", on_delete=models.CASCADE)
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"Review by {self.user.name} - {self.rating} Stars"  # Use 'name' instead of 'username'
  # models.py (Customer.models)

from django.db import models
from Customer.models import Customer, OrderItem
from Homechef.models import HomeChef_registration

class ChatMessage(models.Model):
    sender = models.CharField(max_length=10, choices=[('customer', 'Customer'), ('chef', 'Chef')])
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    chef = models.ForeignKey(HomeChef_registration, on_delete=models.CASCADE, null=True, blank=True)
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)

    def _str_(self):
        return f"{self.sender} to {self.chef.full_name} on {self.timestamp}"