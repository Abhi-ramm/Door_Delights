from django.shortcuts import render, redirect


def admin_dashboard(request):
    return render(request, 'adminindex.html')


from Homechef.models import HomeChef_registration

def homechef_list(request):
    """
    Fetch and display all registered HomeChefs for the admin.
    """
    homechefs = HomeChef_registration.objects.all()
    return render(request, 'view_chefrequests.html', {'homechefs': homechefs})

from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.conf import settings
from Homechef.models import HomeChef_registration

def approve_or_reject_homechef(request, chef_id):
    chef = get_object_or_404(HomeChef_registration, id=chef_id)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "approved":
            chef.status = "Approved"
            chef.save()
            subject = "HomeChef Registration Approved"
            message = f"""Dear {chef.full_name},

Congratulations! 🎉 Your HomeChef registration with Door Delights has been approved. 

You can now log in to your account, add dishes, and start receiving orders! If you need any assistance, feel free to reach out to our support team.

Best Regards,  
Door Delights Team"""

        elif action == "rejected":
            subject = "HomeChef Registration Rejected"
            message = f"""Dear {chef.full_name},

We regret to inform you that your Door Delights HomeChef registration has been rejected.

Best Regards,  
Door Delights Team"""
            
            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [chef.email], fail_silently=False)
            except BadHeaderError:
                return HttpResponse("Invalid header found.")
            except Exception as e:
                print(f"Email failed: {e}")

            chef.delete()  # Delete the rejected chef
            return redirect("dadmin:homechef_list")

        # Send email for approval
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [chef.email], fail_silently=False)
        except BadHeaderError:
            return HttpResponse("Invalid header found.")
        except Exception as e:
            print(f"Email failed: {e}")

    return redirect("dadmin:approved_homechef_list")

def approved_homechef_list(request):
    """
    Fetch and display only approved HomeChefs for the admin.
    """
    homechefs = HomeChef_registration.objects.filter(status="Approved")  # Only approved chefs
    return render(request, 'view_approvedchef.html', {'homechefs': homechefs})


from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib import messages
from Delivery_Boys.models import DeliveryBoy


def delivery_boy_list(request):
    """
    Fetches all delivery boys and displays them.
    """
    delivery_boys = DeliveryBoy.objects.all()
    return render(request, "view_deliveryboys.html", {"delivery_boys": delivery_boys})

from django.core.mail import send_mail, BadHeaderError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse


def update_delivery_boy_status(request, boy_id, status):
    """
    Approves or rejects a delivery boy and sends an email notification.
    If rejected, the delivery boy's details are removed from the database.
    """
    delivery_boy = get_object_or_404(DeliveryBoy, id=boy_id)
    
    subject = "Your Delivery Boy Registration Status"
    
    if status == "approved":
        # Approve the delivery boy
        delivery_boy.status = "approved"
        delivery_boy.save()
        
        message = (
            f"Dear {delivery_boy.full_name},\n\n"
            "Congratulations! Your registration has been APPROVED.\n\n"
            "You can now log in to your account and start your food delivery work. Safe ride!\n\n"
            "Best Regards,\nDoor Delights Team"
        )

    elif status == "rejected":
        # Prepare the rejection email before deleting
        message = (
            f"Dear {delivery_boy.full_name},\n\n"
            "We regret to inform you that your registration has been REJECTED.\n\n"
            "For more information, please contact our support team.\n\n"
            "Best Regards,\nDoor Delights Team"
        )

        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [delivery_boy.email], fail_silently=False)
            print("Rejection email sent successfully!")
        except BadHeaderError:
            return HttpResponse("Invalid header found.")
        except Exception as e:
            print(f"Email failed: {e}")

        # Delete the rejected delivery boy
        delivery_boy.delete()
        return redirect("dadmin:delivery_boy_list")  # Adjust the redirect URL as needed

    # Send email for approval
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [delivery_boy.email], fail_silently=False)
        print("Approval email sent successfully!")
    except BadHeaderError:
        return HttpResponse("Invalid header found.")
    except Exception as e:
        print(f"Email failed: {e}")

    messages.success(request, f"Delivery boy {delivery_boy.full_name} has been {status}.")
    return redirect("dadmin:approved_delivery_boys")  # Adjust the redirect URL as needed


def approved_delivery_boys(request):
    """
    Fetch and display all approved delivery boys.
    """
    approved_boys = DeliveryBoy.objects.filter(status="approved")  # Get only approved delivery boys
    return render(request, "view_approveddboys.html", {"approved_boys": approved_boys})


from django.shortcuts import render
from Customer.models import Customer

def customers(request):
    # Fetch all customers from the database
    customers = Customer.objects.all()
    
    # Pass all customers to the template
    return render(request, 'view_customers.html', {
        'customers': customers
    })

from django.shortcuts import render
from Customer.models import Complaint

def view_complaints(request):
    complaints = Complaint.objects.select_related('customer', 'order', 'home_chef', 'delivery_boy').all()
    
    context = {
        'complaints': complaints
    }
    return render(request, 'complaint.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages


def update_complaint_status(request, complaint_id):
    if request.method == "POST":
        complaint = get_object_or_404(Complaint, id=complaint_id)
        new_status = request.POST.get("status")

        if new_status in ["pending", "resolved", "rejected"]:
            complaint.status = new_status
            complaint.save()
            messages.success(request, "Complaint status updated successfully!")
        else:
            messages.error(request, "Invalid status update!")

    return redirect("dadmin:view_complaints")  # Redirect to the complaints list page

# views.py
from django.shortcuts import render, redirect
from .models import AdminUser

def signup_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = AdminUser.objects.create(email=email, password=password)
        return redirect('dadmin:signin_view')
    return render(request, 'asignup.html')

def signin_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = AdminUser.objects.get(email=email, password=password)
            request.session['user_id'] = user.id
            return redirect('dadmin:admin_dashboard')
        except AdminUser.DoesNotExist:
            pass
    return render(request, 'asignin.html')

# views.py
from django.shortcuts import render, redirect
from .models import AdminUser

def signup_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = AdminUser.objects.create(email=email, password=password)
        return redirect('dadmin:signin_view')
    return render(request, 'asignup.html')

def signin_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = AdminUser.objects.get(email=email, password=password)
            request.session['user_id'] = user.id
            return redirect('dadmin:admin_dashboard')
        except AdminUser.DoesNotExist:
            pass
    return render(request, 'asignin.html')

def signout_view(request):
    request.session.flush()
    return redirect('dadmin:signin_view')

from django.shortcuts import render
from Customer.models import Review

def view_reviews(request):
    reviews = Review.objects.select_related('product', 'user', 'product__chef').all()  # Fetch related fields
    return render(request, 'view_rating.html', {'reviews': reviews})

from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum, Count, F
from Customer.models import Checkout, OrderItem
from Delivery_Boys.models import DeliveryAssignment

def daily_report(request):
    # Use Django's timezone-aware local date
    today = timezone.localdate()

    # All orders for today
    orders = Checkout.objects.filter(created_at__date=today)

    # Total revenue for today
    total_today = orders.aggregate(total=Sum('total_amount'))['total'] or 0

    # Top 5 products sold today
    top_products = OrderItem.objects.filter(order__created_at__date=today)\
        .values(product_name=F('product__name'))\
        .annotate(total_sold=Sum('quantity'))\
        .order_by('-total_sold')[:5]

    # Top 5 homechefs based on products sold
    top_chefs = OrderItem.objects.filter(order__created_at__date=today)\
        .values(chef_name=F('product__chef__full_name'))\
        .annotate(total_sold=Sum('quantity'))\
        .order_by('-total_sold')[:5]

    # Top 5 customers based on number of orders
    top_customers = Checkout.objects.filter(created_at__date=today)\
        .values(customer_name=F('customer__name'))\
        .annotate(order_count=Count('id'))\
        .order_by('-order_count')[:5]

    # Top 5 delivery boys based on number of assignments
    top_deliveryboys = DeliveryAssignment.objects.filter(order__created_at__date=today)\
        .values(delivery_boy_name=F('delivery_boy__full_name'))\
        .annotate(assign_count=Count('id'))\
        .order_by('-assign_count')[:5]

    return render(request, 'daily_report.html', {
        'orders': orders,
        'total_today': total_today,
        'top_products': top_products,
        'top_chefs': top_chefs,
        'top_customers': top_customers,
        'top_deliveryboys': top_deliveryboys,
    })


