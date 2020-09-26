from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework import permissions, status
from rest_framework.response import Response
from .serializers import UserPasswordResetSerializer

class UserPasswordResetView(GenericAPIView):
    """
    Calls Django Auth Serializer save method.

    Accepts the following POST parameters: phone
    Returns the success/fail message.
    """
    serializer_class = UserPasswordResetSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        # Create a serializer with request.data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        # Return the success message with OK HTTP status
        return Response(
            {"detail": _("Password reset code has been sent.")},
            status=status.HTTP_200_OK
        )
