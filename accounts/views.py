from django.shortcuts import render,redirect
from .models import *
from django.db.models import Q
from django.contrib import messages
from .utils import generateRandomToken,sendEmailToken,sendOTPtoEmail
from django.http import HttpResponse
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
import random
# Create your views here.

def login_page(request):
    if request.method == "POST":
        email=request.POST.get('email')
        password=request.POST.get('password')

        hotel_user=HotelUser.objects.get(email=email)
        if not hotel_user:
            messages.error(request,"wrong username kindly recheck username")
            return redirect('login_page')
        
        if not hotel_user.is_verified:
            messages.warning(request, "Account not verified")
            return redirect('login_page')
        
        hotel_user=authenticate(username=hotel_user.username,password=password)

        if hotel_user:
            messages.success(request," User verfied")
            login(request,hotel_user)
            return redirect('/')
        else:
            messages.error(request,"Invaild credentials")
            return redirect('login_page')
    return render(request,'login.html')

def register_page(request):
    if request.method =="POST":
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        email=request.POST.get('email')
        phone_number=request.POST.get('phone_number')
        password=request.POST.get('password')
        hotel_user=HotelUser.objects.filter(
            Q(email=email) | Q(phone_number=phone_number)
        )
        if hotel_user.exists():
            messages.error(request,"Account exist with email or phone_number")
            return redirect('register_page')
        hotel_user = HotelUser.objects.create(username=phone_number,
                                first_name=first_name,
                                last_name=last_name,
                                email=email,
                                phone_number=phone_number,
                                email_token=generateRandomToken())
        hotel_user.set_password(password)
        hotel_user.save()
        sendEmailToken(email,hotel_user.email_token)
        messages.success(request,"email sent to your registered email address")
        return redirect('register_page')
        
        
    return render(request,'register.html')

def verify_email_token(request,token):
    try:
        hotel_user=HotelUser.objects.get(email_token=token)
        hotel_user.is_verified=True
        hotel_user.save()
        messages.success(request,"email verfied")
        return redirect('login_page')
    except Exception as e:
        return HttpResponse("Invaild token")
    
def send_otp(request,email):
    hotel_user=HotelUser.objects.filter(email=email)
    if not hotel_user.exists():
        messages.error(request,"Invaild email address")
        return redirect('login_page')
    otp=random.randint(1000,9999)
    hotel_user.update(otp=otp)
    #hotel_user.save()
    sendOTPtoEmail(email,otp)
    return redirect(f'/accounts/verify_otp/{email}')

def verify_otp(request,email):
    if request.method=="POST":
        otp=request.POST.get('otp')
        hotel_user=HotelUser.objects.get(email=email)

        if otp==hotel_user.otp:
            messages.success(request,"login success")
            login(request,hotel_user)
            return redirect('/')
        else:
            messages.error(request,'Invaild OTP')
            return redirect('verify_otp',email=email)
    return render(request,'verify_otp.html')