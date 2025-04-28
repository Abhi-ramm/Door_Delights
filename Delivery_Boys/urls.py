from django.urls import path
from . import views

app_name = 'deliveryboys'  # Use lowercase for consistency

urlpatterns = [
    path('', views.register_delivery_boy, name='register_delivery_boy'),
    path('registration_success/', views.registration_success, name='registration_success'),# Empty path for homepage
    path('delivery_boy_signin/', views.delivery_boy_signin, name='delivery_boy_signin'),
    path('boys_dashboard/', views.boys_dashboard, name='boys_dashboard'),
    path('logout/', views.logout, name='logout'),
    path("delivery_boy_profile/", views.delivery_boy_profile, name="delivery_boy_profile"),
    path('assigned_delivery_boy/<int:delivery_boy_id>/', views.assigned_delivery_boy, name='assigned_delivery_boy'),
     path('update_order_status/<int:order_id>/', views.update_order_status, name='update_order_status'),
]
