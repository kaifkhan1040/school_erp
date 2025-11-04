from rest_framework import serializers
from .models import Task,Attachment,TaskComment,TaskReopenRequest,TaskActivityLog

class AttachmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attachment
        fields = ['id', 'file', 'description', 'uploaded_by','uploaded_at']
        read_only_fields = ['uploaded_by', 'uploaded_at']

    def to_representation(self, instance):
        """
        Customize the output (read) — show full designation details.
        """
        rep = super().to_representation(instance)
        if instance.uploaded_by:
            rep['uploaded_by'] = {
                'id': instance.uploaded_by.id,
                'name': instance.uploaded_by.email,
            }
        else:
            rep['uploaded_by'] = None
        return rep

class TaskActivityLogSerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = TaskActivityLog
        fields = ['id', 'action', 'action_display', 'message', 'user', 'created_at']

    def to_representation(self, instance):
        """
        Customize the output (read) — show full designation details.
        """
        rep = super().to_representation(instance)
        if instance.user:
            rep['user'] = {
                'id': instance.user.id,
                'name': instance.user.email,
            }
        else:
            rep['user'] = None
        return rep


class TaskReopenRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskReopenRequest
        fields = '__all__'

    def to_representation(self, instance):
        """
        Customize the output (read) — show full designation details.
        """
        rep = super().to_representation(instance)
        if instance.user:
            rep['user'] = {
                'id': instance.user.id,
                'name': instance.user.email,
            }
        else:
            rep['user'] = None
        return rep



class CommentSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = TaskComment
        fields = ['id', 'task', 'user', 'content', 'attachments', 'created_at']
        read_only_fields = ['user', 'created_at']

    def to_representation(self, instance):
        """
        Customize the output (read) — show full designation details.
        """
        rep = super().to_representation(instance)
        if instance.user:
            rep['user'] = {
                'id': instance.user.id,
                'name': instance.user.email,
            }
        else:
            rep['user'] = None
        return rep





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
        if instance.assigned_to:
            rep['assigned_to'] = {
                'id': instance.assigned_to.id,
                'name': instance.assigned_to.email,
                'superuser':True
            }
        else:
            rep['assigned_to'] = None
        return rep
