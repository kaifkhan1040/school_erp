from collections import namedtuple
from functools import partial
from .serializers import PasswordChangeSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth import login, authenticate
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError

User = namedtuple('User', ['email', 'password', 'first_name', 'last_name','mobile'])
def _parse_data(data, cls):
    """
    Generic function for parse user data using
    specified validator on `cls` keyword parameter.
    Raises: ValidationError exception if
    some errors found when data is validated.
    Returns the validated data.
    """
    serializer = cls(data=data)
    if not serializer.is_valid():
        raise ValidationError(serializer.errors)
    return serializer.validated_data

parse_auth_password_change_data = partial(_parse_data, cls=PasswordChangeSerializer)
def auth_password_change(request):
    """
    params: request
    return: data
    """
    data = parse_auth_password_change_data(request.data)
    return data