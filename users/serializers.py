from .models import CustomUser,Designation
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

class UserSerializer(ModelSerializer):
    """
    User Serializer
    """
    class Meta:
        model = CustomUser
        fields = (
            'id', 'email', 'first_name',  'last_name', 'is_staff', 'is_active', 
            'is_superuser','role','designation'
        )
        depth=1
        extra_kwargs = {'password': {'write_only': True}, 
                        'last_login': {'read_only': True}, 'is_superuser': {'read_only': True}}
        

class DesignationSerializer(ModelSerializer):
    class Meta:
        model=Designation
        fields="__all__"

class PasswordChangeSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        min_length=6,
        max_length=128,
        error_messages={'required': 'Please enter a valid password.',
                        'blank': 'Please enter a valid password.',
                        'null': 'Please enter a valid password.',
                        'min_length': 'Password should have minimum 6 characters.'}
    )