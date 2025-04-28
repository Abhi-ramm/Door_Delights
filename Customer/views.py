from django.shortcuts import render

def customer_home(request):
    products = Product.objects.all().order_by('?')[:6]  # Fetch exactly 6 random products
    approved_chefs = HomeChef_registration.objects.filter(status='Approved')[:3]

    return render(request, 'index.html', {'products': products, 'approved_chefs': approved_chefs})
    

def about(request):
    print("Rendering About Page")  # Debugging
    return render(request, 'about.html')

from django.shortcuts import render

from django.shortcuts import render
from django.shortcuts import render
from Homechef.models import Product

def shop(request):
    products = Product.objects.all()

    categorized_products = {
        'Breakfast': products.filter(category='Breakfast'),
        'Lunch': products.filter(category='Lunch'),
        'Evening Snack': products.filter(category='Evening Snack'),
        'Dinner': products.filter(category='Dinner'),
    }

    return render(request, 'shop.html', {'categorized_products': categorized_products})

from Homechef.models import HomeChef_registration

def guest(request):
    products = Product.objects.all().order_by('?')[:6]  # Fetch exactly 6 random products
    approved_chefs = HomeChef_registration.objects.filter(status='Approved')[:3]

    return render(request, 'guest.html', {'products': products, 'approved_chefs': approved_chefs})

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Customer
import re

def signup(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        password = request.POST.get("password")

        # Validation
        if not name or not email or not phone or not address or not password:
            messages.error(request, "All fields are required.")
            return render(request, "signup.html")

        # Email validation
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            messages.error(request, "Enter a valid email address.")
            return render(request, "signup.html")

        # Phone validation
        if len(phone) != 10 or not phone.isdigit():
            messages.error(request, "Enter a valid 10-digit phone number.")
            return render(request, "signup.html")

        # Password validation
        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return render(request, "signup.html")

        # Check if email or phone number is already registered
        if Customer.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, "signup.html")

        if Customer.objects.filter(phone=phone).exists():
            messages.error(request, "Phone number is already registered.")
            return render(request, "signup.html")

        # Save Customer (password stored as plain text)
        customer = Customer(name=name, email=email, phone=phone, address=address, password=password)
        customer.save()

        
        return redirect("customer:customer_home")  # Redirect after signup

    return render(request, "signup.html")
def signin(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        # Check if user exists
        user = Customer.objects.filter(email=email, password=password).first()
        if user:
            request.session["user_id"] = user.id  # Store user ID
            request.session["customer_email"] = user.email  # Store email for profile retrieval
            request.session.modified = True  # Ensure session gets saved
            
            return redirect("customer:customer_home")  
        else:
            messages.error(request, "Invalid email or password!")
            return redirect("customer:signin")

    return render(request, "signin.html")


def signout(request):
    request.session.flush()  # Clear session
    
    return redirect("customer:signin")

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from Customer.models import Customer,OrderItem

def customer_profile(request):
    # Check if customer is logged in
    customer_id = request.session.get("user_id")  # Fetch customer ID from session

    if not customer_id:  # If not logged in, redirect to sign-in
        messages.error(request, "Please log in to access your profile.")
        return redirect("customer:signin")

    # Get customer data safely
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == "POST":
        customer.name = request.POST["name"]
        customer.phone = request.POST["phone"]
        customer.address = request.POST["address"]
        customer.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("customer:customer_profile")

    return render(request, "profile.html", {"customer": customer})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Cart, CartItem, Checkout, Customer
from Homechef.models import Product  

def view_cart(request):
    cart = None  

    if request.user.is_authenticated:
        customer = get_object_or_404(Customer, user=request.user)
        cart = Cart.objects.filter(user=customer).first()
    else:
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart = Cart.objects.filter(id=cart_id).first()

    if cart:
        cart_items = CartItem.objects.filter(cart=cart).select_related('product')
        total_price = sum(item.get_total_price() for item in cart_items)
        total_supercoins = sum(item.get_total_supercoins() for item in cart_items)
    else:
        cart_items = []
        total_price = 0
        total_supercoins = 0

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_supercoins': total_supercoins,
    })

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.GET.get('quantity', 1))

    if product.stock == 0:
        messages.error(request, "⚠ This item is out of stock.")
        return redirect('customer:shop')

    if request.user.is_authenticated:
        customer = get_object_or_404(Customer, user=request.user)
        cart, created = Cart.objects.get_or_create(user=customer)
    else:
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart = Cart.objects.filter(id=cart_id).first()
        else:
            cart = Cart.objects.create(user=None)  
            request.session['cart_id'] = cart.id

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity

    if cart_item.quantity > product.stock:
        messages.warning(request, f"⚠ Only {product.stock} units available.")
        cart_item.quantity = product.stock

    cart_item.save()
    messages.success(request, "Item added to cart.")
    
    return redirect('customer:view_cart')

def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)

    if request.method == "POST":
        try:
            new_quantity = int(request.POST.get('quantity', 1))

            if cart_item.product.stock == 0:
                messages.error(request, "⚠ This item is no longer available.")
                cart_item.delete()  
                return redirect('customer:view_cart')

            if new_quantity < 1:
                messages.error(request, "⚠ Quantity cannot be less than 1.")
                return redirect('customer:view_cart')

            if new_quantity > cart_item.product.stock:
                messages.warning(request, f"⚠ Only {cart_item.product.stock} units available.")
                new_quantity = cart_item.product.stock  

            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, "Cart updated successfully.")
        except ValueError:
            messages.error(request, "Invalid quantity.")

    return redirect('customer:view_cart')

def remove_from_cart(request, item_id):
    if request.user.is_authenticated:
        cart = get_object_or_404(Cart, user=request.user)
    else:
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart = get_object_or_404(Cart, id=cart_id)
        else:
            messages.error(request, "No cart found.")
            return redirect('customer:shop')

    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()

    messages.success(request, "Item removed from cart.")
    return redirect('customer:view_cart')

def checkout(request):
    customer_id = request.session.get("user_id")  

    if not customer_id:  
        messages.error(request, "Please log in to access your profile.")
        return redirect("customer:signin")

    customer = get_object_or_404(Customer, id=customer_id)

    cart_id = request.session.get("cart_id")
    if not cart_id:
        messages.error(request, "Your cart is empty. Please add items before checkout.")
        return redirect("customer:view_cart")

    cart = get_object_or_404(Cart, id=cart_id)
    cart_items = CartItem.objects.filter(cart=cart)
    total_price = sum(item.get_total_price() for item in cart_items)

    for item in cart_items:
        if item.product.stock < item.quantity:
            messages.error(request, f"Not enough stock for {item.product.name}. Available: {item.product.stock}")
            return redirect("customer:view_cart")

    user_details = {
        "name": customer.name,
        "email": customer.email,
        "address": customer.address,
        "phone": customer.phone,
    }

    supercoins_balance = customer.supercoins  
    max_supercoin_discount = min(supercoins_balance * 10, 100)  

    if request.method == "POST":
        supercoins_used = int(request.POST.get("supercoins_used", 0))
        payment_method = request.POST.get("payment_method", "supercoins")

        if supercoins_used > supercoins_balance:
            messages.error(request, "You don't have enough SuperCoins.")
            return redirect("customer:view_cart")
        
        if supercoins_used * 10 > 100:  
            messages.error(request, "You can use a maximum of ₹100 worth of SuperCoins.")
            return redirect("customer:view_cart")

        supercoin_value = supercoins_used * 10  
        final_amount = max(total_price - supercoin_value, 0)  

        payment_status = "paid" if payment_method in ["supercoins", "card"] else "pending"

        # ✅ Fix: Remove "cart=cart" since the Checkout model does not have a cart field
        checkout = Checkout.objects.create(
            customer=customer,
            total_amount=total_price,
            supercoins_used=supercoins_used,
            payment_method=payment_method,
            amount_to_pay=final_amount,
            payment_status=payment_status,
            status="pending",
        )

        customer.supercoins -= supercoins_used

        for item in cart_items:
            product = item.product
            product.stock -= item.quantity
            product.save()

            # ✅ Create OrderItem for each cart item
            OrderItem.objects.create(
                order=checkout,
                product=product,
                quantity=item.quantity,
                price_at_purchase=item.get_total_price(),
            )

        earned_supercoins = total_price // 100  
        customer.supercoins += earned_supercoins
        customer.save()

        # ✅ Clear the cart after placing the order
        cart_items.delete()
        request.session.pop("cart_id", None)

        messages.success(request, f"Order placed successfully! You earned {earned_supercoins} SuperCoins. Pay ₹{final_amount} using {payment_method}.")
        return redirect("customer:my_orders")

    return render(
        request,
        "checkout.html",
        {
            "cart_items": cart_items,
            "total_price": total_price,
            "supercoins_balance": supercoins_balance,
            "max_supercoin_discount": max_supercoin_discount,
            "user_details": user_details,  
        },
    )


from django.shortcuts import render, get_object_or_404
from .models import Customer, Checkout, OrderItem, ChatMessage

def my_orders(request):
    customer_id = request.session.get("user_id")

    if not customer_id:
        return render(request, 'my_order.html', {'orders': []})

    customer = get_object_or_404(Customer, id=customer_id)
    checkouts = Checkout.objects.filter(customer=customer).order_by('-created_at')

    orders = []
    for checkout in checkouts:
        order_items = OrderItem.objects.filter(order=checkout).select_related('product', 'product__chef')

        formatted_items = []

        for item in order_items:
            chef = item.product.chef
            unread_count = 0
            if chef:
                unread_count = ChatMessage.objects.filter(
                    customer=customer,
                    chef=chef,
                    sender='chef',
                    order_item=item,
                    is_read=False
                ).count()

            formatted_items.append({
                "id": item.id,
                "name": item.product.name,
                "image_url": item.product.image.url if item.product.image else None,
                "quantity": item.quantity,
                "price": item.price_at_purchase,
                "chef_name": chef.full_name if chef else "Unknown",
                "chef_id": chef.id if chef else None,
                "unread_count": unread_count,  # Pass the unread count here
            })

        orders.append({
            'checkout': checkout,
            'order_items': formatted_items,
        })

    return render(request, 'my_order.html', {'orders': orders})



def contact(request):
    print("Rendering About Page")  # Debugging
    return render(request, 'contact.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Complaint
from Customer.models import Customer, Checkout
from Homechef.models import HomeChef_registration
from Delivery_Boys.models import DeliveryBoy, DeliveryAssignment

def submit_complaint(request):
    customer_id = request.session.get("user_id")  # Fetch logged-in customer ID
    if not customer_id:
        messages.error(request, "Please log in to submit complaints.")
        return redirect("customer:signin")

    customer = Customer.objects.get(id=customer_id)  
    orders = Checkout.objects.filter(customer=customer, status="completed")  # Fetch only completed orders

    if request.method == "POST":
        order_id = request.POST.get("order")
        category = request.POST.get("category")
        complaint_text = request.POST.get("complaint_text")

        if not order_id or not category or not complaint_text:
            messages.error(request, "All fields are required.")
            return redirect("submit_complaint")

        try:
            selected_order = Checkout.objects.get(id=order_id, customer=customer, status="completed")
        except Checkout.DoesNotExist:
            messages.error(request, "Invalid order selection.")
            return redirect("submit_complaint")

        home_chef = selected_order.order_items.first().product.chef if selected_order.order_items.exists() else None
        delivery_assignment = DeliveryAssignment.objects.filter(order=selected_order).first()
        delivery_boy = delivery_assignment.delivery_boy if delivery_assignment else None

        Complaint.objects.create(
            customer=customer,
            order=selected_order,
            home_chef=home_chef if category == "homechef" else None,
            delivery_boy=delivery_boy if category == "delivery boy" else None,
            category=category,
            complaint_text=complaint_text
        )

        messages.success(request, "Complaint submitted successfully.")
        return redirect("customer:view_complaints")

    return render(
        request,
        "complaints.html",
        {"customer": customer, "orders": orders},
    )


from django.http import JsonResponse
from Customer.models import Checkout
from Homechef.models import HomeChef_registration
from Delivery_Boys.models import DeliveryAssignment
from django.http import JsonResponse


def get_order_details(request, order_id):
    try:
        order = OrderItem.objects.get(id=order_id)
        data = {
            "home_chef": order.home_chef.name if order.home_chef else "",
            "delivery_boy": order.delivery_boy.name if order.delivery_boy else "",
        }
        return JsonResponse(data)
    except OrderItem.DoesNotExist:
        return JsonResponse({"error": "Order not found"}, status=404)

from django.shortcuts import render
from django.contrib import messages
from .models import Complaint
from Customer.models import Customer

def view_complaints(request):
    customer_id = request.session.get("user_id")  # Fetch logged-in customer ID
    if not customer_id:
        messages.error(request, "Please log in to view your complaints.")
        return redirect("customer:signin")

    customer = Customer.objects.get(id=customer_id)  
    complaints = Complaint.objects.filter(customer=customer).select_related("order", "home_chef", "delivery_boy")

    return render(request, "view_complaints.html", {"complaints": complaints})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, Review, Customer
def review_page(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    latest_reviews = product.reviews.all().order_by('-created_at')[:3]
    return render(request, 'rating.html', {
        'product': product,
        'latest_reviews': latest_reviews
    })



def add_review(request, product_id):
    """Handles review submission for a product."""
    
    customer_id = request.session.get("user_id")  
    if not customer_id:
        messages.error(request, "Please log in to submit a review.")
        return redirect("customer:signin")

    customer = get_object_or_404(Customer, id=customer_id)
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if not rating or not comment:
            messages.error(request, "Rating and comment are required.")
            return redirect('customer:review_page', product_id=product_id)

        # Create the review using the correct customer reference
        Review.objects.create(product=product, user=customer, rating=rating, comment=comment)
        messages.success(request, "Review added successfully!")

        return redirect('customer:shop')  

    return render(request, "rating.html", {"product": product})


from django.shortcuts import render, get_object_or_404, redirect
from .models import Customer, ChatMessage, OrderItem

def chat_with_chef(request, order_item_id):
    customer_id = request.session.get('user_id')
    if not customer_id:
        return redirect('customer:signin')

    customer = get_object_or_404(Customer, id=customer_id)
    order_item = get_object_or_404(OrderItem, id=order_item_id)

    # Safely get the chef from the product
    chef = getattr(order_item.product, 'chef', None)
    if not chef:
        return render(request, 'chat.html', {
            'messages': [],
            'chef': None,
            'order_item': order_item,
            'error': "Chef not assigned to this product."
        })

    # Mark unread chef messages as read
    ChatMessage.objects.filter(
        order_item=order_item,
        customer=customer,
        chef=chef,
        sender='chef',
        is_read=False
    ).update(is_read=True)

    # ✅ Ensure both order_item and customer+chef match
    messages = ChatMessage.objects.filter(
        order_item=order_item,
        customer=customer,
        chef=chef
    ).order_by('timestamp')

    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            ChatMessage.objects.create(
                customer=customer,
                chef=chef,
                order_item=order_item,
                sender='customer',
                message=message
            )
            return redirect('customer:chat_with_chef', order_item_id=order_item.id)

    return render(request, 'chat.html', {
        'messages': messages,
        'chef': chef,
        'order_item': order_item
    })