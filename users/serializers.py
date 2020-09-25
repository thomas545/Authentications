from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, exceptions
from phonenumber_field.serializerfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber as DjangoPhoneNumber
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer

from .models import PhoneNumber, PhoneNumberVerification
from .utils import generate_key, send_verification_sms
User = get_user_model()


class UserRegisterSerializer(RegisterSerializer):
    email = None
    phone = PhoneNumberField(required=True)

    def validate_phone(self, phone):
        if phone and User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError(
                _("A user is already registered with this Phone Number.")
            )
        return phone

    def custom_signup(self, request, user):
        user.phone = self.validated_data.get('phone', '')
        user.save()
        send_verification_sms(user)

class UserLoginSerializer(LoginSerializer):
    email = None

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')

        user = None

        if 'allauth' in settings.INSTALLED_APPS:
            from allauth.account import app_settings

            # Authentication through email
            if app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.EMAIL:
                user = self._validate_email(email, password)

            # Authentication through username
            elif app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.USERNAME:
                user = self._validate_username(username, password)

            # Authentication through either username or email
            else:
                user = self._validate_username_email(username, email, password)

        else:
            # Authentication without using allauth
            if email:
                try:
                    username = User.objects.get(email__iexact=email).get_username()
                except User.DoesNotExist:
                    pass

            if username:
                user = self._validate_username_email(username, '', password)

        # Did we get back an active user?
        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Wrong username or password.')
            raise exceptions.ValidationError(msg)

        # If required, is the email verified?
        if 'dj_rest_auth.registration' in settings.INSTALLED_APPS:
            from allauth.account import app_settings
            if app_settings.EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.MANDATORY:
                email_address = user.emailaddress_set.get(email=user.email)
                if not email_address.verified:
                    raise serializers.ValidationError(_('E-mail is not verified.'))

        phone = DjangoPhoneNumber.from_string(phone_number=username)
        if getattr(settings, "PHONE_NUMBER_VERIFICATION", False) and phone.is_valid():
            phone_number = PhoneNumber.objects.filter(phone=username)
            if not phone_number:
                raise serializers.ValidationError(_("You don't have a phone number."))

            if phone_number and not phone_number.first().verified:
                raise serializers.ValidationError(_('Phone Number is not verified.'))
        else:
            if not PhoneNumber.objects.filter(user=user, verified=True, phone=user.phone):
                raise serializers.ValidationError(_('Your phone number is not verified.'))

        attrs['user'] = user
        return attrs