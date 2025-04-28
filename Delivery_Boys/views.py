from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import DeliveryBoy
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

import re


def register_delivery_boy(request):
    """
    Handles delivery boy registration with validation and inserts into the database.
    """
    if request.method == "POST":
        full_name = request.POST.get("fullName").strip()
        phone = request.POST.get("phone").strip()
        email = request.POST.get("email").strip()
        aadhaar = request.POST.get("aadhaar").strip()
        license_number = request.POST.get("license").strip()
        password = request.POST.get("password").strip()
        confirm_password = request.POST.get("confirmPassword").strip()
        photo = request.FILES.get("photo")

        errors = {}

        # Validate empty fields
        if not all([full_name, phone, email, aadhaar, license_number, password, confirm_password, photo]):
            errors["exception"] = "All fields are required!"

        # Phone validation (must be exactly 10 digits)
        if not re.fullmatch(r"^[6-9]\d{9}$", phone):
            errors["phone"] = "Enter a valid 10-digit phone number!"

        # Aadhaar validation (must be exactly 12 digits)
        if not re.fullmatch(r"^\d{12}$", aadhaar):
            errors["aadhaar"] = "Enter a valid 12-digit Aadhaar number!"

        # Password validation (min 8 characters, at least 1 letter and 1 number)
        if len(password) < 8 or not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
            errors["password"] = "Password must be at least 8 characters long and contain at least 1 letter and 1 number!"

        # Confirm password validation
        if password != confirm_password:
            errors["confirmPassword"] = "Passwords do not match!"

        # Email validation
        try:
            validate_email(email)
        except ValidationError:
            errors["email"] = "Invalid email format!"

        # Unique field checks
        if DeliveryBoy.objects.filter(phone_number=phone).exists():
            errors["phone"] = "Phone number already registered!"

        if DeliveryBoy.objects.filter(email=email).exists():
            errors["email"] = "Email already registered!"

        if DeliveryBoy.objects.filter(aadhaar_number=aadhaar).exists():
            errors["aadhaar"] = "Aadhaar number already in use!"

        if DeliveryBoy.objects.filter(license_number=license_number).exists():
            errors["license"] = "License number already registered!"

        # If errors exist, re-render the form with errors
        if errors:
            return render(request, "dboyssignup.html", {"errors": errors, "form_data": request.POST})

        # Save delivery boy data without hashing the password
        delivery_boy = DeliveryBoy(
            full_name=full_name,
            phone_number=phone,
            email=email,
            aadhaar_number=aadhaar,
            license_number=license_number,
            photo=photo,
            password=password,  # No hashing
            status="pending",
        )
        delivery_boy.save()

        return redirect("deliveryboys:registration_success")

    return render(request, "dboyssignup.html")


def registration_success(request):
    """
    Render the registration success page.
    """
    return render(request, 'dbreg_success.html')

from django.shortcuts import render, redirect
from .models import DeliveryBoy

def delivery_boy_signin(request):
    errors = {}

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            delivery_boy = DeliveryBoy.objects.get(email=email)

            if delivery_boy.password == password:  # Plain text password check
                request.session["delivery_boy_id"] = delivery_boy.id  # Save session
                return redirect("deliveryboys:boys_dashboard")  # Redirect to dashboard
            else:
                errors["password"] = "Invalid password."
        
        except DeliveryBoy.DoesNotExist:
            errors["email"] = "Email not found."

    return render(request, "dboyssignin.html", {"errors": errors})

from django.shortcuts import render, redirect
from .models import DeliveryBoy

def boys_dashboard(request):
    if "delivery_boy_id" not in request.session:
        return redirect("delivery_boy_signin")  # Redirect if not logged in

    delivery_boy = DeliveryBoy.objects.get(id=request.session["delivery_boy_id"])
    
    return render(request, "boys_dashboard.html", {"delivery_boy": delivery_boy})

from django.shortcuts import redirect

def logout(request):
    if "delivery_boy_id" in request.session:
        del request.session["delivery_boy_id"]  # Remove session data
    return redirect("deliveryboys:delivery_boy_signin")  # Redirect to login page


from django.shortcuts import render, redirect
from .models import DeliveryBoy
from django.core.files.storage import default_storage

def delivery_boy_profile(request):
    if "delivery_boy_id" not in request.session:
        return redirect("delivery_boy_signin")  # Redirect if not logged in

    delivery_boy = DeliveryBoy.objects.get(id=request.session["delivery_boy_id"])

    if request.method == "POST":
        # Update fields from the form
        delivery_boy.full_name = request.POST.get("full_name")
        delivery_boy.phone_number = request.POST.get("phone_number")
        delivery_boy.availability_status = request.POST.get("availability_status")

        # Handle profile image upload
        if "photo" in request.FILES:
            if delivery_boy.photo:  # Delete old photo if exists
                default_storage.delete(delivery_boy.photo.path)
            delivery_boy.photo = request.FILES["photo"]

        delivery_boy.save()
        return redirect("deliveryboys:delivery_boy_profile")  # Refresh page after update

    return render(request, "boys_profile.html", {"delivery_boy": delivery_boy})


from django.shortcuts import render, get_object_or_404
from Delivery_Boys.models import DeliveryAssignment, DeliveryBoy
from Customer.models import Checkout

def assigned_delivery_boy(request, delivery_boy_id):
    # Fetch the delivery boy using the delivery_boy_id
    delivery_boy = get_object_or_404(DeliveryBoy, id=delivery_boy_id)

    # Get the related assignments for the delivery boy
    assignments = DeliveryAssignment.objects.filter(delivery_boy=delivery_boy)

    # Prepare order details
    order_details = []
    for assignment in assignments:
        order = assignment.order  # This is the related Checkout (order)
        order_details.append({
            "order_id": order.id,
            "customer_name": order.customer.name,
            "delivery_address": order.customer.address,
            "order_status": order.status,
            "assigned_status": assignment.status,
            "payment_status": order.payment_status,
        })

    return render(request, 'view_assigned_orders.html', {
        'delivery_boy': delivery_boy,
        'order_details': order_details
    })

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Checkout, DeliveryAssignment
from Delivery_Boys.models import DeliveryBoy

def update_order_status(request, order_id):
    order = get_object_or_404(Checkout, id=order_id)
    
    if request.method == "POST":
        # Fetch the related delivery assignment for the order
        assignment = DeliveryAssignment.objects.filter(order=order).first()
        if not assignment:
            messages.error(request, f"No assignment found for Order #{order.id}.")
            return redirect('deliveryboys:assigned_delivery_orders')

        # Update assigned_status in DeliveryAssignment
        assigned_status = request.POST.get("assigned_status")
        if assigned_status:
            assignment.status = assigned_status
            assignment.save()
            messages.success(request, f"Order #{order.id} assigned status updated successfully!")
        
        # Update payment_status in Checkout (Order)
        payment_status = request.POST.get("payment_status")
        if payment_status:
            order.payment_status = payment_status
            order.save()
            messages.success(request, f"Order #{order.id} payment status updated successfully!")

        # Update status in Checkout (Order)
        order_status = request.POST.get("order_status")
        if order_status:
            order.status = order_status
            order.save()
            messages.success(request, f"Order #{order.id} status updated successfully!")

    # After updating, redirect back to the delivery boy's assigned orders page
    return redirect('deliveryboys:assigned_delivery_boy', delivery_boy_id=assignment.delivery_boy.id)
