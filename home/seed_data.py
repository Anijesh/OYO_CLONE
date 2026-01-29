import os
import sys
import django

# Add project root to Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Setup Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "oyo_clone.settings")
django.setup()

# Now it's safe to import Django models
from django.contrib.auth.models import User
from accounts.models import *
from faker import Faker
fake = Faker()
import random

def createUser(count=100):
    for _ in range(count):
        email = fake.unique.email()
        HotelVendor.objects.create(
            email=email,
            business_name=fake.company(),
            username=email,
            first_name=fake.first_name(),
            phone_number=str(random.randint(1111111111, 9999999999)),
            is_verified=True
        )


from random import choice
def createHotel(count=100):
    vendors = list(HotelVendor.objects.all())
    amenities = list(Ameneties.objects.all())

    if not vendors:
        print("❌ No vendors found. Create users first.")
        return

    for _ in range(count):
        hotel_vendor = choice(vendors)

        hotel = Hotel.objects.create(
            hotel_name=fake.company(),
            hotel_description=fake.text(),
            hotel_slug=fake.slug(),
            hotel_owner=hotel_vendor,
            hotel_price=random.randint(500, 5000),
            hotel_offer_price=random.randint(300, 4000),
            hotel_location=fake.city(),
            is_active=True
        )

        hotel.ameneties.set(amenities)

        
if __name__ == "__main__":
    print("Seeding started...")

    createUser(200)    # 200 vendors/users
    createHotel(100)  # 100 hotels

    print("✅ Seeding finished")
