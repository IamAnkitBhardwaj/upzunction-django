from django.urls import path
from . import views

urlpatterns = [
    # This is the crucial line that connects your homepage
    path('', views.home_view, name='home'),
    
    # All other URLs for your application
    path('register/', views.register_request_view, name='register_request'),
    path('register/verify/', views.register_verify_view, name='register_verify'),
    path('post/new/', views.create_post_view, name='create_post'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    
    path('post/<int:post_id>/edit/', views.edit_post_view, name='edit_post'),
    path('post/<int:post_id>/delete/', views.delete_post_view, name='delete_post'),
    path('post/<int:post_id>/deactivate/', views.deactivate_post_view, name='deactivate_post'),
    
    path('post/<int:post_id>/send_message/', views.send_message_view, name='send_message'),
    path('message/<int:message_id>/approve/', views.approve_message_view, name='approve_message'),
    
    path('password-reset/', views.password_reset_request_view, name='password_reset_request'),
    path('password-reset/otp/', views.password_reset_otp_view, name='password_reset_otp'),
    path('password-reset/new/', views.password_reset_new_password_view, name='password_reset_new'),
    
    path('terms-of-service/', views.terms_of_service_view, name='terms_of_service'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
]



