from django.db import models


from django.contrib.auth.models import User


# Create your models here.

class HostelUser(User):
    profile_picture =models.ImageField(upload_to='profile')
    phone_number=models.CharField(unique=True,max_length=10)
    email_token=models.CharField(max_length=100,null=True,blank=True)
    otp =models.CharField(max_length=10,null=True,blank=True)


class HotelVender(User):
    phone_number=models.CharField(unique=True,max_length=10)
    profile_picture=models.ImageField(upload_to='profile')
    email_token=models.CharField(max_length=100,null=True,blank=True)
    otp =models.CharField(max_length=10,null=True,blank=True)



class Ameneties(models.Model):
    name=models.CharField(max_length=1000)
    icon=models.ImageField(upload_to='hotels')

class Hotel(models.Model):
    hotel_name=models.CharField(max_length=200)
    hotel_location=models.CharField(max_length=200)
    description=models.TextField()
    hotel_slug=models.SlugField(max_length=1000,unique=True)
    hotel_owner=models.ForeignKey(HotelVender,on_delete=models.CASCADE,related_name='hotels')
    ameneties=models.ManyToManyField(Ameneties)
    hotel_price=models.FloatField()
    hotel_offer_price=models.FloatField()
    is_active=models.BooleanField(default=True)

class HotelImages(models.Model):
    hotel=models.ForeignKey(Hotel,on_delete=models.CASCADE,related_name='hotel_images')
    image=models.ImageField(upload_to='hotels')

class HotelManager(models.Model):
    hotel=models.ForeignKey(Hotel,on_delete=models.CASCADE,related_name='hotel_manager')
    manager_name=models.CharField(max_length=200)
    manager_contact=models.CharField(max_length=100)