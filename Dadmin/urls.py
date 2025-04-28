from django.urls import path
from . import views

app_name = 'dadmin'  # Use lowercase for consistency


urlpatterns = [
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),# Empty path for homepage
    path('homechef_list/', views.homechef_list, name='homechef_list'),
    path("approve_or_reject_homechef/<int:chef_id>/", views.approve_or_reject_homechef, name="approve_or_reject_homechef"),
    path('approved_homechef_list/', views.approved_homechef_list, name='approved_homechef_list'),
    path('delivery_boy_list/', views.delivery_boy_list, name='delivery_boy_list'),
    path("update_delivery_boy_status/<int:boy_id>/<str:status>/", views.update_delivery_boy_status, name="update_delivery_boy_status"),
    path('approved_delivery_boys/', views.approved_delivery_boys, name='approved_delivery_boys'),
    path('daily_report/', views.daily_report, name='daily_report'),
    path('customers/', views.customers, name='customers'),
    path('view_complaints/', views.view_complaints, name='view_complaints'),
    path('update_complaint_status/<int:complaint_id>/',views.update_complaint_status, name="update_complaint_status"),
    path('signup_view/', views.signup_view, name='signup_view'),
    path('', views.signin_view, name='signin_view'),
    path('signout_view/', views.signout_view, name='signout_view'),
    path('view_reviews/', views.view_reviews, name='view_reviews'),
]
