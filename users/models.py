from random import randint
from datetime import timedelta
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from .utils import generate_code


class User(AbstractUser):
    """
    User Model
    Username and password are required. Other fields are optional.
    """

    phone = PhoneNumberField(
        verbose_name=_("phone Number"), unique=True, blank=True, null=True
    )


class PhoneNumber(models.Model):
    user = models.ForeignKey(
        get_user_model(), related_name="phone_numbers", on_delete=models.CASCADE
    )
    phone = PhoneNumberField(
        verbose_name=_("Phone Number"), unique=settings.UNIQUE_PHONE_NUMBER
    )
    verified = models.BooleanField(verbose_name=_("Verified"), default=False)
    primary = models.BooleanField(verbose_name=_("Primary"), default=False)

    def __str__(self):
        return self.phone.as_e164


class PhoneNumberVerification(models.Model):
    phone_number = models.ForeignKey(
        PhoneNumber, related_name="phone_verifications", on_delete=models.CASCADE
    )
    key = models.IntegerField(verbose_name=_("Key"), blank=True, null=True)
    sent = models.DateTimeField(verbose_name=_("Sent"), null=True)
    created = models.DateTimeField(verbose_name=_("Created"), default=timezone.now)

    def __str__(self):
        return str(self.key)


class ResetPasswordCode(models.Model):
    user = user = models.ForeignKey(
        get_user_model(), related_name="reset_codes", on_delete=models.CASCADE
    )
    code = models.IntegerField(verbose_name=_("Reset Password Code"), unique=True)
    sent = models.DateTimeField(verbose_name=_("Sent"), null=True)
    created = models.DateTimeField(verbose_name=_("Created"), default=timezone.now)

    @property
    def code_expired(self):
        try:
            return timezone.now() > (
                self.sent + timedelta(minutes=getattr(settings, "EXPIRED_RESET_CODE", 10))
            )
        except Exception:
            return None

    # def save(self, *args, **kwargs):
    #     if not self.code:
    #         self.code = randint(1000000, 9999999)
    #     if self.code and self.code_expired:
    #         self.code = randint(1000000, 9999999)
    #     super(ResetPasswordCode, self).save(*args, **kwargs)

