from django.shortcuts import render, redirect
from .models import HomeChef_registration

def homechef_signup(request):
    """
    Process the HomeChef registration request.
    On GET: render the registration form.
    On POST: validate data, save the record, and redirect to a success page.
    """
    if request.method == 'POST':
        # Retrieve form data
        photo = request.FILES.get('photo')
        full_name = request.POST.get('fullName', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        aadhaar = request.POST.get('aadhaar', '').strip()
        dish = request.POST.get('dish', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirmPassword', '')

        errors = {}

        # Validate photo: must exist, be JPG or PNG, and less than 10 MB
        if not photo:
            errors['photo'] = "Please upload a photo."
        else:
            file_type = photo.content_type
            file_size = photo.size
            if file_type not in ['image/jpeg', 'image/png']:
                errors['photo'] = "Only JPG or PNG files are allowed."
            elif file_size > 10 * 1024 * 1024:
                errors['photo'] = "Photo must be less than 10 MB."

        # Validate full name
        if not full_name:
            errors['fullName'] = "Full name is required."

        # Validate phone: must be 10 digits
        if not phone or not phone.isdigit() or len(phone) != 10:
            errors['phone'] = "Enter a valid 10-digit phone number."

        # Validate email
        if not email:
            errors['email'] = "Email is required."

        # Validate Aadhaar: must be 12 digits
        if not aadhaar or not aadhaar.isdigit() or len(aadhaar) != 12:
            errors['aadhaar'] = "Enter a valid 12-digit Aadhaar number."

        # Validate dish field
        if not dish:
            errors['dish'] = "At least one dish is required."

        # Validate passwords
        if not password:
            errors['password'] = "Password is required."
        if not confirm_password:
            errors['confirmPassword'] = "Please confirm your password."
        if password and confirm_password and password != confirm_password:
            errors['confirmPassword'] = "Passwords do not match."

        # If errors, re-render the form with errors and previous data
        if errors:
            context = {
                'errors': errors,
                'form_data': {
                    'fullName': full_name,
                    'phone': phone,
                    'email': email,
                    'aadhaar': aadhaar,
                    'dish': dish,
                }
            }
            return render(request, 'chefsignup.html', context)

        # Optionally, clean the dish names (remove extra spaces, etc.)
        dish_list = [d.strip() for d in dish.split(',') if d.strip()]
        dish_clean = ", ".join(dish_list)

        # Save the record
        try:
            new_signup = HomeChef_registration(
                photo=photo,
                full_name=full_name,
                phone_number=phone,
                email=email,
                aadhaar_number=aadhaar,
                dish=dish_clean,
                password=password  # Plain text; do not use in production!
            )
            new_signup.save()
        except Exception as e:
            errors['exception'] = f"Error saving data: {e}"
            context = {
                'errors': errors,
                'form_data': {
                    'fullName': full_name,
                    'phone': phone,
                    'email': email,
                    'aadhaar': aadhaar,
                    'dish': dish,
                }
            }
            return render(request, 'chefsignup.html', context)

        # On success, redirect to the registration success page
        return redirect('homechef:registration_success')

    # For GET requests, simply render the form
    return render(request, 'chefsignup.html')


def registration_success(request):
    """
    Render the registration success page.
    """
    return render(request, 'reg_success.html')

from django.shortcuts import render, redirect
from .models import HomeChef_registration

def homechef_signin(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        errors = {}

        if not email:
            errors['email'] = "Email is required."
        if not password:
            errors['password'] = "Password is required."

        if errors:
            return render(request, 'chefsignin.html', {'errors': errors})

        try:
            user = HomeChef_registration.objects.get(email=email)

            # Allow only approved users to log in
            if user.status == "Pending":
                errors['email'] = "Your account is pending approval. Please wait for admin approval."
                return render(request, 'chefsignin.html', {'errors': errors})
            
            if user.status == "Rejected":
                errors['email'] = "Your account has been rejected. Please contact support."
                return render(request, 'chefsignin.html', {'errors': errors})

            # Check if the password matches (Plain text, as per your request)
            if password == user.password:  
                request.session['homechef_id'] = user.id
                return redirect('homechef:chef_dashboard')  # Redirect to the dashboard
            else:
                errors['password'] = "Invalid email or password."

        except HomeChef_registration.DoesNotExist:
            errors['email'] = "No account found with this email."

        return render(request, 'chefsignin.html', {'errors': errors})

    return render(request, 'chefsignin.html')

from django.shortcuts import render, get_object_or_404, redirect

from Customer.models import Customer
from Homechef.models import HomeChef_registration
def chef_dashboard(request):
    if 'homechef_id' not in request.session:
        return redirect('homechef:chefsignin')

    chef = get_object_or_404(HomeChef_registration, id=request.session['homechef_id'])

    # Get all distinct customers who have chatted with this chef
    customer_ids = ChatMessage.objects.filter(chef=chef).values_list('customer_id', flat=True).distinct()
    customers = Customer.objects.filter(id__in=customer_ids)

    # Get the last message and unread count for each customer
    customer_chats = []
    for customer in customers:
        last_message = ChatMessage.objects.filter(chef=chef, customer=customer).order_by('-timestamp').first()
        unread_count = ChatMessage.objects.filter(
            chef=chef, customer=customer, sender='customer', is_read=False
        ).count()
        customer_chats.append({
            'customer': customer,
            'last_message': last_message,
            'unread_count': unread_count
        })

    context = {
        'chef': chef,
        'customer_chats': customer_chats
    }
    return render(request, 'chef_dashboard.html', context)


from django.shortcuts import render, redirect
from .models import HomeChef_registration

def chef_logout(request):
    """
    Logs out the HomeChef by clearing the session.
    """
    if 'homechef_id' in request.session:
        del request.session['homechef_id']  # Remove session data
    
    return redirect('homechef:homechef_signin')  # Redirect to login page

from django.shortcuts import render, get_object_or_404, redirect
from .models import HomeChef_registration

def homechef_profile(request):
    if 'homechef_id' not in request.session:
        return redirect('homechef:homechef_signin')  # Redirect if not logged in

    # Fetch the logged-in home chef's details
    chef = get_object_or_404(HomeChef_registration, id=request.session['homechef_id'])

    if request.method == 'POST':
        chef.full_name = request.POST.get('full_name', chef.full_name)
        chef.phone_number = request.POST.get('phone_number', chef.phone_number)
        chef.dish = request.POST.get('dish', chef.dish)

        if 'photo' in request.FILES:
            chef.photo = request.FILES['photo']

        chef.save()
        return redirect('homechef:homechef_profile')  # Reload the profile page after saving

    return render(request, 'chef_profile.html', {'chef': chef})

from django.shortcuts import render, redirect
from .models import Product, HomeChef_registration
from django.contrib import messages

def add_product(request):
    if 'homechef_id' not in request.session:
        return redirect('homechef:homechef_signin')  # Redirect to login if not signed in

    chef = HomeChef_registration.objects.get(id=request.session['homechef_id'])

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        supercoins = request.POST.get('supercoins', 0)
        stock = request.POST.get('stock', 0)
        category = request.POST.get('category', 'Breakfast')  # Get selected category
        image = request.FILES.get('image')

        if name and price and image:
            Product.objects.create(
                chef=chef,
                name=name,
                description=description,
                price=price,
                supercoins=supercoins,
                stock=stock,
                category=category,
                image=image
            )
            messages.success(request, "Product added successfully!")
            return redirect('homechef:view_products')  # Redirect after adding product

    return render(request, 'add_product.html')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, HomeChef_registration

# View Products (Already added in the previous step)
def view_products(request):
    if 'homechef_id' not in request.session:
        return redirect('homechef:homechef_signin')

    chef = HomeChef_registration.objects.get(id=request.session['homechef_id'])
    products = Product.objects.filter(chef=chef)

    return render(request, 'view_product.html', {'products': products})

# Edit Product
def edit_product(request, product_id):
    if 'homechef_id' not in request.session:
        return redirect('homechef:homechef_signin')

    product = get_object_or_404(Product, id=product_id, chef_id=request.session['homechef_id'])

    if request.method == 'POST':
        product.name = request.POST.get('name', product.name)
        product.description = request.POST.get('description', product.description)
        product.price = request.POST.get('price', product.price)
        product.supercoins = request.POST.get('supercoins', product.supercoins)
        product.stock = request.POST.get('stock', product.stock)
        product.category = request.POST.get('category', product.category)

        if 'image' in request.FILES:
            product.image = request.FILES['image']

        product.save()
        messages.success(request, "Product updated successfully!")
        return redirect('homechef:view_products')

    return render(request, 'edit_product.html', {'product': product})

# Delete Product
def delete_product(request, product_id):
    if 'homechef_id' not in request.session:
        return redirect('homechef:homechef_signin')

    product = get_object_or_404(Product, id=product_id, chef_id=request.session['homechef_id'])
    product.delete()
    messages.success(request, "Product deleted successfully!")
    return redirect('homechef:view_products')

from django.shortcuts import render, get_object_or_404, redirect
from Customer.models import OrderItem, Checkout, Customer
from Homechef.models import Product, HomeChef_registration  

def chef_orders(request):
    # ✅ Ensure homechef is logged in using session data
    if 'homechef_id' not in request.session:
        return redirect('homechef:homechef_signin')  # Redirect if not logged in

    # ✅ Get the logged-in homechef
    chef = get_object_or_404(HomeChef_registration, id=request.session['homechef_id'])

    # ✅ Fetch only products created by this homechef
    chef_products = Product.objects.filter(chef=chef)

    # ✅ Get order items related to this homechef's products
    order_items = OrderItem.objects.filter(product__in=chef_products)

    # ✅ Get unique orders containing those order items
    orders = Checkout.objects.filter(order_items__in=order_items).distinct()

    # ✅ Process the orders
    order_data = []
    for order in orders:
        # ✅ Fetch only this chef's order items in the order
        items = order.order_items.filter(product__in=chef_products)

        order_data.append({
            'order_id': order.id,
            'customer_name': order.customer.name if order.customer else "Unknown",  # Handle missing customer
            'items': [
                {
                    'product_name': item.product.name, 
                    'quantity': item.quantity, 
                    'total_price': item.price_at_purchase * item.quantity
                } 
                for item in items
            ],
            'total_price': sum(item.price_at_purchase for item in items),
            'payment_method': dict(Checkout.PAYMENT_METHOD_CHOICES).get(order.payment_method, 'Unknown'),  
            'payment_status': dict(Checkout.PAYMENT_STATUS_CHOICES).get(order.payment_status, 'Pending'),  
            'order_status': dict(Checkout.STATUS_CHOICES).get(order.status, 'Pending'),  
            'order_date': order.created_at.strftime('%Y-%m-%d'),
        })

    return render(request, 'view_orders.html', {'orders': order_data})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from Delivery_Boys.models import DeliveryBoy, DeliveryAssignment
from Customer.models import Checkout

def assign_delivery(request, schedule_id):
    schedule = get_object_or_404(Checkout, id=schedule_id)
    assignment = DeliveryAssignment.objects.filter(order=schedule).first()

    # Fetch available delivery boys
    delivery_boys = DeliveryBoy.objects.filter(status="approved", availability_status="available")

    if request.method == "POST":
        # Get the selected delivery boy and status
        delivery_boy_id = request.POST.get("delivery_boy_id")
        status = request.POST.get("status")

        if delivery_boy_id:
            delivery_boy = get_object_or_404(DeliveryBoy, id=delivery_boy_id)

            if assignment:
                assignment.delivery_boy = delivery_boy
                assignment.status = status
                assignment.save()
            else:
                # Create a new assignment if one doesn't exist
                DeliveryAssignment.objects.create(
                    order=schedule,
                    delivery_boy=delivery_boy,
                    status=status
                )

            messages.success(request, f"Delivery boy {delivery_boy.full_name} assigned to schedule {schedule.id} successfully!")
            return redirect('homechef:chef_orders')  # Adjust to your schedule list page

    return render(request, 'assign_delivery.html', {'schedule': schedule, 'assignment': assignment, 'delivery_boys': delivery_boys})
# views.py

from django.shortcuts import render
from Customer.models import Customer

def customer_details(request):
    # Fetch all customers from the database
    customers = Customer.objects.all()
    
    # Pass all customers to the template
    return render(request, 'view_user.html', {
        'customers': customers
    })

from django.shortcuts import render
from Delivery_Boys.models import DeliveryBoy

def approved_delivery_boys(request):
    # Fetch all approved delivery boys
    approved_boys = DeliveryBoy.objects.filter(status='approved')
    
    # Pass the approved boys to the template
    return render(request, 'view_boys.html', {
        'approved_boys': approved_boys
    })
from django.shortcuts import render
from Customer.models import Checkout, OrderItem
from Homechef.models import Product

def completed_orders(request):
    # Get the logged-in HomeChef ID from session (or however you're tracking login)
    homechef_id = request.session.get('homechef_id')

    if not homechef_id:
        return render(request, 'error.html', {'message': 'Home Chef not logged in'})

    # Get all products created by this HomeChef
    homechef_products = Product.objects.filter(chef_id=homechef_id)

    # Get OrderItems that include any of those products
    order_items = OrderItem.objects.filter(product__in=homechef_products)

    # Get completed orders associated with those order items
    order_ids = order_items.values_list('order_id', flat=True).distinct()
    orders = Checkout.objects.filter(id__in=order_ids, status='completed').distinct()

    return render(request, 'complete_order.html', {
        'orders': orders
    })

from django.shortcuts import render
from Customer.models import Checkout, OrderItem
from Homechef.models import Product, HomeChef_registration

def pending_orders(request):
    # Assuming the logged-in home chef is stored in session
    homechef_id = request.session.get('homechef_id')
    
    if not homechef_id:
        return render(request, 'error.html', {'message': 'Home Chef not logged in'})

    # Get all products created by the logged-in HomeChef
    homechef_products = Product.objects.filter(chef_id=homechef_id)

    # Get all order items that include any of the HomeChef's products
    order_items = OrderItem.objects.filter(product__in=homechef_products)

    # Get the orders associated with those order items and filter pending ones
    order_ids = order_items.values_list('order_id', flat=True).distinct()
    orders = Checkout.objects.filter(id__in=order_ids, status='pending').distinct()

    return render(request, 'pending_order.html', {'orders': orders})

from django.shortcuts import render
from django.http import HttpResponse
from openpyxl import Workbook
from datetime import datetime
from Customer.models import Checkout, OrderItem
from Homechef.models import Product

from django.db.models import Sum

def daily_orders(request):
    # Get the logged-in HomeChef ID from session
    homechef_id = request.session.get('homechef_id')
    if not homechef_id:
        return render(request, 'error.html', {'message': 'Home Chef not logged in'})

    # Get today's date
    today = datetime.today().date()

    # Get products of this HomeChef
    homechef_products = Product.objects.filter(chef_id=homechef_id)

    # Get order items of these products created today
    order_items = OrderItem.objects.filter(
        product__in=homechef_products,
        order__created_at__date=today
    )

    # Get distinct order IDs
    order_ids = order_items.values_list('order_id', flat=True).distinct()

    # Fetch orders matching those IDs
    orders = Checkout.objects.filter(id__in=order_ids)

    # Calculate total amount only for this chef’s products in today's orders
    total_today = order_items.aggregate(total=Sum('price_at_purchase'))['total'] or 0

    # If Excel download requested
    if request.GET.get('download') == 'excel':
        wb = Workbook()
        ws = wb.active
        ws.title = "Daily Orders"

        # Headers
        headers = ['Order ID', 'Order Date', 'Customer Name', 'Products', 'Total Price', 'Payment Method', 'Payment Status', 'Order Status', 'Assigned Delivery Boy']
        ws.append(headers)

        for order in orders:
            order_date = order.created_at.strftime('%Y-%m-%d') if order.created_at else ''

            # Get only this homechef's items in this order
            chef_items = order.order_items.filter(product__chef_id=homechef_id)
            product_names = ', '.join([f"{item.product.name} (x{item.quantity})" for item in chef_items])
            order_total = sum(item.price_at_purchase for item in chef_items)

            row = [
                order.id,
                order_date,
                order.customer.name,
                product_names,
                order_total,
                order.payment_method,
                order.payment_status,
                order.status,
                order.deliveryassignment_set.first().delivery_boy.full_name if order.deliveryassignment_set.first() else 'Not assigned'
            ]
            ws.append(row)

        # Excel Response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="daily_orders.xlsx"'
        wb.save(response)
        return response

    # Render HTML
    return render(request, 'daily_orders.html', {
        'orders': orders,
        'total_today': total_today,
    })


from django.shortcuts import render
from Homechef.models import Product
from Customer.models import Review  # assuming it's in Customer app or wherever Review is defined

def homechef_reviews(request):
    # Get HomeChef ID from session
    homechef_id = request.session.get('homechef_id')
    if not homechef_id:
        return render(request, 'error.html', {'message': 'You must be logged in as a Home Chef to view reviews.'})

    # Fetch products added by the logged-in HomeChef
    products = Product.objects.filter(chef_id=homechef_id).prefetch_related('reviews')

    return render(request, 'rating_feedback.html', {
        'products': products
    })
from django.shortcuts import render, get_object_or_404, redirect
from Customer.models import ChatMessage
from Homechef.models import HomeChef_registration
from Customer.models import Customer

from Customer.models import OrderItem

def chat_with_customer(request, customer_id):
    if 'homechef_id' not in request.session:
        return redirect('homechef:chefsignin')

    chef = get_object_or_404(HomeChef_registration, id=request.session['homechef_id'])
    customer = get_object_or_404(Customer, id=customer_id)

    messages = ChatMessage.objects.filter(customer=customer, chef=chef).order_by('timestamp')

    # ✅ Only mark unread customer messages as read
    messages.filter(sender='customer').update(is_read=True)

    unread_count = messages.filter(sender='customer', is_read=False).count()

    order_items = OrderItem.objects.filter(
        order__customer=customer,
        product__chef=chef
    ).select_related('order', 'product')

    if request.method == 'POST':
        message_content = request.POST.get('message')
        order_item_id = request.POST.get('order_item_id')
        if message_content and order_item_id:
            order_item = get_object_or_404(OrderItem, id=order_item_id)
            ChatMessage.objects.create(
                sender='chef',
                message=message_content,
                chef=chef,
                customer=customer,
                order_item=order_item,
                is_read=False  # ✅ Message will be unread for customer
            )
            return redirect('homechef:chat_with_customer', customer_id=customer.id)

    context = {
        'customer': customer,
        'messages': messages,
        'unread_count': unread_count,
        'order_items': order_items,
    }

    return render(request, 'chat_with_customer.html', context)


