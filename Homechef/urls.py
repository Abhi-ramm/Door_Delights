from django.urls import path
from . import views

app_name = 'Homechef'  # Use lowercase for consistency

urlpatterns = [
    path('', views.homechef_signup, name='homechef_signup'),
    path('homechef_signin/', views.homechef_signin, name='homechef_signin'),
    path('chef_dashboard/', views.chef_dashboard, name='chef_dashboard'),
    path('registration_success/', views.registration_success, name='registration_success'),# Empty path for homepage
    path('chef_logout/', views.chef_logout, name='chef_logout'),  # Logout URL
    path('homechef_profile/', views.homechef_profile, name='homechef_profile'),
    path('add_product/', views.add_product, name='add_product'),
    path('view_products/', views.view_products, name='view_products'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('chef_orders/', views.chef_orders, name='chef_orders'),
    path('assign_delivery/<int:schedule_id>/', views.assign_delivery, name='assign_delivery'),
    path('customer_details/', views.customer_details, name='customer_details'),
    path('approved_delivery_boys/', views.approved_delivery_boys, name='approved_delivery_boys'),
    path('completed_orders/', views.completed_orders, name='completed_orders'),
    path('pending_orders/', views.pending_orders, name='pending_orders'),
    path('daily_orders/', views.daily_orders, name='daily_orders'),
    path('homechef_reviews/', views.homechef_reviews, name='homechef_reviews'),
    path('chat_with_customer/<int:customer_id>/', views.chat_with_customer, name='chat_with_customer'),
]
