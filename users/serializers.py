from .models import CustomUser,Designation
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.fields import ImageField

class RecursiveUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'designation', 'subordinates')

    subordinates = serializers.SerializerMethodField()

    def get_subordinates(self, obj):
        # Prevent infinite recursion by limiting depth
        depth = self.context.get('depth', 0)
        if depth >= 4:  # Stop after 3 levels
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
    image = serializers.ImageField(required=False, allow_null=True)  
    reporting_manager = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        required=False,
        allow_null=True
    )
    total_tasks = serializers.SerializerMethodField()
    completed_tasks = serializers.SerializerMethodField()
    team = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = (
            'id', 'email', 'first_name',  'last_name', 'is_staff', 'is_active', 
            'is_superuser','role','designation','reporting_manager', 'team','is_report','is_task_recive','is_task_create',
            'total_tasks', 'completed_tasks',"image"
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
        
    def get_total_tasks(self, obj):
        return obj.assigned_tasks.count()

    def get_completed_tasks(self, obj):
        return obj.assigned_tasks.filter(status='completed').count()

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
    
    def update(self, instance, validated_data):
    # Prevent is_active from becoming false automatically
        if 'is_active' not in validated_data:
            validated_data['is_active'] = instance.is_active
        return super().update(instance, validated_data)

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



