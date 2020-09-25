from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()


class AuthenticationBackends(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get("username")

        if username is None or password is None:
            return

        try:
            user = UserModel.objects.get(
                Q(username__iexact=username)
                | Q(phone=username)
                | Q(email__iexact=username)
            )
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
        except MultipleObjectsReturned:
            user = UserModel.objects.filter(username=username).first()
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
