from random import randint
from django.utils import timezone



def generate_code():
    return randint(1000000, 9999999)


def generate_key():
    return randint(100000, 999999)


def send_verification_sms(user):
    from .models import PhoneNumber, PhoneNumberVerification
    phone_number = PhoneNumber.objects.create(user=user, phone=user.phone)
    phone_verified = PhoneNumberVerification.objects.create(
        phone_number=phone_number, key=generate_key(), sent=timezone.now()
    )
    # TODO send sms with key
