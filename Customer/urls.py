from django.urls import path
from . import views

app_name = 'customer'  # Use lowercase for consistency

urlpatterns = [
    path('', views.guest, name='guest'),
    path('customer_home', views.customer_home, name='customer_home'),  # Empty path for homepage
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'), 
    path('shop/', views.shop, name='shop'),
    path("signup/", views.signup, name="signup"),
    path("signin/", views.signin, name="signin"),
    path("signout/", views.signout, name="signout"),
    path("customer_profile/", views.customer_profile, name="customer_profile"),
    path('cart/', views.view_cart, name='view_cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update_cart/<int:item_id>/', views.update_cart, name='update_cart'),  # Ensure this line is correct
    path('checkout/', views.checkout, name='checkout'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('submit_complaint/', views.submit_complaint, name='submit_complaint'),
    path("get_order_details/<int:order_id>/", views.get_order_details, name="get_order_details"),
    path('view_complaints/', views.view_complaints, name='view_complaints'),
    path('review/<int:product_id>/', views.review_page, name='review_page'),
    path('add_review/<int:product_id>/', views.add_review, name='add_review'),
    path('chat_with_chef/<int:order_item_id>/', views.chat_with_chef, name='chat_with_chef'),
]
