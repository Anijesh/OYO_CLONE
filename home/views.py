from django.shortcuts import render
from accounts.models import Hotel , HotelBooking, HotelUser
from django.http import HttpResponseRedirect
from django.contrib import messages

# Create your views here.


def index(request):
    hotels = Hotel.objects.all().prefetch_related('hotel_images','ameneties')
    if request.GET.get('search'):
        hotels = hotels.filter(hotel_name__icontains = request.GET.get('search'))
    
    if request.GET.get('sort_by'):
        sort_by = request.GET.get('sort_by')
        if sort_by == "sort_low":
            hotels = hotels.order_by('hotel_offer_price')
        elif sort_by == "sort_high":
            hotels = hotels.order_by('-hotel_offer_price')
    return render(request,'index.html',context={'hotels':hotels[:20]})



from datetime import datetime
def hotel_details(request,slug):
    hotel = Hotel.objects.get(hotel_slug = slug)

    if request.method=='POST':
        start_date_str=request.POST.get('start_date')
        end_date_str=request.POST.get('end_date')
        start_date=datetime.strptime(start_date_str,'%Y-%m-%d')
        end_date=datetime.strptime(end_date_str,'%Y-%m-%d')
        days_count=(end_date-start_date).days
        if(days_count <= 0):
            messages.warning(request,"Invaild Booking date")
            return HttpResponseRedirect(request.path_info)
        if start_date < datetime.now() or end_date < datetime.now():
            messages.error(request, "Dates cannot be in the past")
            return HttpResponseRedirect(request.path_info)

        HotelBooking.objects.create(
            hotel=hotel,
            booking_user=HotelUser.objects.get(id=request.user.id),
            booking_start_date=start_date,
            booking_end_date=end_date,
            price=hotel.hotel_offer_price*days_count,
        )
        messages.success(request,"Booking Successful")
        return HttpResponseRedirect(request.path_info)

    return render(request,'hotel_detail.html',context = {'hotel' : hotel})
