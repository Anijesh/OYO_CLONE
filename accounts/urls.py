from django.contrib import admin
from django.urls import path
from accounts import views

urlpatterns = [
    path('login/',views.login_page,name='login_page'),
    path('register/',views.register_page,name='register_page'),
    path('verify-account/<token>/',views.verify_email_token,name='verify_email_token'),
    path('send_otp/<email>/',views.send_otp,name='send_otp'),
    path('verify_otp/<email>/',views.verify_otp,name='verify_otp')
    ]
