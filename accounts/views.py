from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.db.models import Q
from django.contrib import messages
from .utils import generateRandomToken,sendEmailToken,sendOTPtoEmail,generateSlug
from django.http import HttpResponse,HttpResponseRedirect
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

def verify_email_token(request, token):
    try:
        user = HotelUser.objects.filter(email_token=token).first()
        vendor = HotelVendor.objects.filter(email_token=token).first()

        if user:
            user.is_verified = True
            user.save()
        elif vendor:
            vendor.is_verified = True
            vendor.save()
        else:
            return HttpResponse("Invalid token")

        messages.success(request, "Email verified successfully")
        return redirect('login_page')

    except Exception:
        return HttpResponse("Invalid token")

    
def send_otp(request, email):
    user = HotelUser.objects.filter(email=email).first()
    vendor = HotelVendor.objects.filter(email=email).first()

    if not user and not vendor:
        messages.error(request, "Invalid email address")
        return redirect('login_page')

    otp = random.randint(1000, 9999)

    if user:
        user.otp = otp
        user.save()
    else:
        vendor.otp = otp
        vendor.save()

    sendOTPtoEmail(email, otp)
    return redirect(f'/accounts/verify_otp/{email}')


def verify_otp(request, email):
    if request.method == "POST":
        otp = request.POST.get('otp')

        user = HotelUser.objects.filter(email=email).first()
        vendor = HotelVendor.objects.filter(email=email).first()

        account = user or vendor

        if not account:
            messages.error(request, "Account not found")
            return redirect('login_page')

        if str(account.otp) == str(otp):
            account.otp = None
            account.save()
            login(request, account)
            if account ==user:
                return redirect('/')
            else:
                return redirect('vendor_dashboard')
        else:
            messages.error(request, "Invalid OTP")
            return redirect('verify_otp', email=email)

    return render(request, 'verify_otp.html')

def login_vendor(request):
    if request.method == "POST":
        email=request.POST.get('email')
        password=request.POST.get('password')

        hotel_vendor=HotelVendor.objects.get(email=email)
        if not hotel_vendor:
            messages.error(request,"wrong username kindly recheck username")
            return redirect('login_vendor')
        
        if not hotel_vendor.is_verified:
            messages.warning(request, "Account not verified")
            return redirect('login_vendor')
        
        hotel_vendor=authenticate(username=hotel_vendor.username,password=password)

        if hotel_vendor:
            login(request,hotel_vendor)
            return redirect('vendor_dashboard')
        messages.error(request,"Invaild credentials")
        return redirect('login_vendor')
    return render(request,'vendor/login_vendor.html')

def register_vendor(request):
    if request.method =="POST":
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        business_name=request.POST.get('business_name')
        email=request.POST.get('email')
        phone_number=request.POST.get('phone_number')
        password=request.POST.get('password')
        hotel_vendor=HotelVendor.objects.filter(
            Q(email=email) | Q(phone_number=phone_number)
        )
        if hotel_vendor.exists():
            messages.error(request,"Account exist with email or phone_number")
            return redirect('register_vendor')
        hotel_vendor = HotelVendor.objects.create(username=phone_number,
                                first_name=first_name,
                                last_name=last_name,
                                business_name=business_name,
                                email=email,
                                phone_number=phone_number,
                                email_token=generateRandomToken())
        hotel_vendor.set_password(password)
        hotel_vendor.save()
        sendEmailToken(email,hotel_vendor.email_token)
        messages.success(request,"email sent to your registered email address")
        return redirect('register_vendor')
        
        
    return render(request,'vendor/register_vendor.html')


@login_required(login_url='login_vendor')
def vendor_dashboard(request):
    hotels=Hotel.objects.filter(hotel_owner=request.user)
    return render(request,'vendor/vendor_dashboard.html',context={'hotels':hotels})

@login_required(login_url='login_vendor')
def add_hotel(request):
    if request.method == "POST":
        hotel_name = request.POST.get("hotel_name")
        hotel_location = request.POST.get("hotel_location")
        hotel_description = request.POST.get('hotel_description')
        ameneties_ids = request.POST.getlist('ameneties')
        hotel_price = request.POST.get('hotel_price')
        hotel_offer_price = request.POST.get('hotel_offer_price')
        hotel_slug = generateSlug(hotel_name)

        hotel_vendor = HotelVendor.objects.get(id=request.user.id)
        hotel_obj=Hotel.objects.create(hotel_name=hotel_name,
                                   hotel_location= hotel_location,
                                   hotel_description= hotel_description,
                                   hotel_owner =hotel_vendor,
                                   hotel_price=hotel_price,
                                   hotel_offer_price=hotel_offer_price,
                                   hotel_slug= hotel_slug,
                                   )
        
        for amenetie_id in ameneties_ids:
            amenetie_obj= get_object_or_404(Ameneties, id=amenetie_id)
            hotel_obj.ameneties.add(amenetie_obj)
            hotel_obj.save()
        messages.success(request,'Hotel Created')
        return redirect('/accounts/add_hotel/')
    
    ameneties=Ameneties.objects.all()
    
    return render(request,'vendor/add_hotel.html',context={'ameneties':ameneties})

@login_required(login_url='login_vendor')
def upload_images(request,slug):
    hotel_obj = Hotel.objects.get(hotel_slug = slug)
    if request.method=="POST":
        image=request.FILES['image']
        print(image)
        HotelImages.objects.create(
        hotel = hotel_obj,
        image = image
        )
        return HttpResponseRedirect(request.path_info)
    return render(request,'vendor/upload_images.html',context = {'images' : hotel_obj.hotel_images.all()})

@login_required(login_url='login_vendor')
def delete_image(request, id):
    hotel_image = get_object_or_404(HotelImages, id=id)

    if hotel_image.hotel.hotel_owner.id != request.user.id:
        messages.error(request, "You are not allowed to delete this image")
        return redirect('vendor_dashboard')
    hotel_image.delete()
    messages.success(request, "Hotel image deleted successfully")
    return redirect('vendor_dashboard')

@login_required(login_url='login_vendor')
def edit_hotels(request,slug):
    hotel_obj = Hotel.objects.get(hotel_slug = slug)
    if hotel_obj.hotel_owner.id != request.user.id:
        messages.error(request,"You are not allowed to edit the hotel")
        return redirect('vendor_dashboard')

    if request.method == "POST":
        hotel_name = request.POST.get('hotel_name')
        hotel_description = request.POST.get('hotel_description')
        hotel_price= request.POST.get('hotel_price')
        hotel_offer_price= request.POST.get('hotel_offer_price')
        hotel_location= request.POST.get('hotel_location')
        hotel_obj.hotel_name  = hotel_name
        hotel_obj.hotel_description  = hotel_description
        hotel_obj.hotel_price  = hotel_price
        hotel_obj.hotel_offer_price  = hotel_offer_price
        hotel_obj.hotel_location  = hotel_location
        hotel_obj.save()

        ameneties_ids = request.POST.getlist('ameneties')
        hotel_obj.ameneties.set(ameneties_ids)

        messages.success(request, "Hotel Details Updated")
        return HttpResponseRedirect(request.path_info)
    all_ameneties = Ameneties.objects.all()
    
    return render(request,'vendor/edit_hotels.html',context = {'hotel' : hotel_obj,'ameneties' : all_ameneties})

def logout_view(request):
    logout(request)
    return redirect('/')