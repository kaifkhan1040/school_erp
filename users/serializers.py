from .models import CustomUser,Designation
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer


class RecursiveUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'designation', 'subordinates')

    subordinates = serializers.SerializerMethodField()

    def get_subordinates(self, obj):
        # Prevent infinite recursion by limiting depth
        depth = self.context.get('depth', 0)
        if depth >= 3:  # Stop after 3 levels
            return []
        
        subordinates = obj.subordinates.all()
        if not subordinates:
            return []

        serializer = RecursiveUserSerializer(
            subordinates,
            many=True,
            context={'depth': depth + 1}  # increment recursion depth
        )
        return serializer.data
    
class UserSerializer(ModelSerializer):
    """
    User Serializer
    """
    # designation = serializers.PrimaryKeyRelatedField(
    #     queryset=Designation.objects.all(),
    #     required=False,
    #     allow_null=True
    # )
    designation = serializers.PrimaryKeyRelatedField(
        queryset=Designation.objects.all(),
        required=False,
        allow_null=True
    )

    reporting_manager = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        required=False,
        allow_null=True
    )
    team = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = (
            'id', 'email', 'first_name',  'last_name', 'is_staff', 'is_active', 
            'is_superuser','role','designation','reporting_manager', 'team','is_report','is_task_recive','is_task_create'
        )
        # depth=1
        extra_kwargs = {'password': {'write_only': True}, 
                        'last_login': {'read_only': True}, 'is_superuser': {'read_only': True}}
    # def get_team(self, obj):
    #     """Fetch full recursive team tree."""
    #     return RecursiveUserSerializer(obj.subordinates.all(), many=True).data
    
    def get_team(self, obj):
        """Fetch recursive team structure with safe depth control."""
        return RecursiveUserSerializer(
            obj.subordinates.all(),
            many=True,
            context={'depth': 0}  # start recursion from depth 0
        ).data
        
    def to_representation(self, instance):
        """
        Customize the output (read) — show full designation details.
        """
        rep = super().to_representation(instance)
        if instance.designation:
            rep['designation'] = {
                'id': instance.designation.id,
                'name': instance.designation.name
            }
        else:
            rep['designation'] = None
        if instance.reporting_manager:
            rep['reporting_manager'] = {
                'id': instance.reporting_manager.id,
                'email': instance.reporting_manager.email
            }
        else:
            rep['reporting_manager'] = None
        return rep

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



