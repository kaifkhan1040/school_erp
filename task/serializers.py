from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']


    def update(self, instance, validated_data):
        user = self.context['request'].user
        new_status = validated_data.get('status', instance.status)

        # If user is superadmin → can change everything
        if user.is_superuser == True:
            return super().update(instance, validated_data)
        else:
            if instance.status == 'completed' and new_status != instance.status:
                raise serializers.ValidationError({"message":"You cannot change status once you completed the task."})
            return super().update(instance, validated_data)
        
    def to_representation(self, instance):
        """
        Customize the output (read) — show full designation details.
        """
        rep = super().to_representation(instance)
        if instance.created_by:
            rep['created_by'] = {
                'id': instance.created_by.id,
                'name': instance.created_by.email,
                'superuser':True
            }
        else:
            rep['created_by'] = None
        return rep
