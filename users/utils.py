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


def send_reset_password_code(user):
    from .models import ResetPasswordCode

    reset_code, code = ResetPasswordCode.objects.filter(user=user), None
    if reset_code and not reset_code.first().code_expired:
        code = reset_code.first().code
    elif reset_code and reset_code.first().code_expired:
        reset_code.update(code=generate_code(), sent=timezone.now())
        code = reset_code.first().code
    else:
        reset_code = ResetPasswordCode.objects.create(
            user=user, sent=timezone.now(), code=generate_code()
        )
        code = reset_code.code

    print("code ->> ", code)
    # TODO send sms to user with code
