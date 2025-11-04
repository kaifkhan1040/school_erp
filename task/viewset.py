from rest_framework.viewsets import ModelViewSet
from django.conf import settings
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from base import response
from constants import CONFIG, CONST_REPORT_MAIL

from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .utils import log_task_activity
from rest_framework import viewsets, permissions
from .models import Task,TaskComment,Attachment
from .serializers import TaskSerializer,CommentSerializer,AttachmentSerializer,TaskReopenRequestSerializer,\
    TaskActivityLogSerializer
from rest_framework.response import Response
from rest_framework import status

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().select_related('created_by', 'assigned_to').prefetch_related('comments', 'attachments')
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    parser_classes = (JSONParser, MultiPartParser)

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status')
        assigned_to = self.request.query_params.get('assigned_to')
        if status:
            queryset = queryset.filter(status=status)
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        return queryset

    # def get_queryset(self):
    #     user = self.request.user
    #     # Superadmin & Superuser → can see all tasks
    #     if user.role in ['superadmin', 'superuser']:
    #         return Task.objects.all()
    #     # Normal user → can see only their tasks
    #     return Task.objects.filter(assigned_to=user)

    def perform_create(self, serializer):
        user = self.request.user
        task=serializer.save(created_by=user)
        log_task_activity(task, self.request.user, 'created', f"Task '{task.title}' created.")

    def perform_update(self, serializer):
        old_task = self.get_object()
        new_task = serializer.save()

        # Detect changes
        changes = []
        if old_task.status != new_task.status:
            changes.append(f"Status changed from '{old_task.status}' to '{new_task.status}'.")
            log_task_activity(new_task, self.request.user, 'status_changed', changes[-1])

        if old_task.assigned_to != new_task.assigned_to:
            old_name = old_task.assigned_to.get_full_name() if old_task.assigned_to else 'None'
            new_name = new_task.assigned_to.get_full_name() if new_task.assigned_to else 'None'
            changes.append(f"Assigned changed from '{old_name}' to '{new_name}'.")
            log_task_activity(new_task, self.request.user, 'assigned', changes[-1])

        if not changes:
            log_task_activity(new_task, self.request.user, 'updated', f"Task '{new_task.title}' updated.")

    @action(detail=True, methods=['get', 'post'], url_path='comments')
    def comments(self, request, pk=None):
        task = self.get_object()

        if request.method == 'GET':
            comments = task.comments.all().select_related('user')
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = CommentSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(user=request.user, task=task)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['get'], url_path='logs')
    def logs(self, request, pk=None):
        task = self.get_object()
        if request.method == 'GET':
            comments = task.activity_logs.all()
            serializer = TaskActivityLogSerializer(comments, many=True)
            return Response(serializer.data)
        
    @action(detail=True, methods=['get', 'post'], url_path='attachments')
    def attachments(self, request, pk=None):
        task = self.get_object()

        if request.method == 'GET':
            attachments = task.attachments.all().select_related('uploaded_by')
            serializer = AttachmentSerializer(attachments, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = AttachmentSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(uploaded_by=request.user, task=task)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['get', 'post'], url_path='reopen')
    def reopen(self, request, pk=None):
        task = self.get_object()

        if request.method == 'GET':
            attachments = task.reopen.all()
            serializer = TaskReopenRequestSerializer(attachments, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = TaskReopenRequestSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(user=request.user, task=task)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = TaskComment.objects.all().select_related('task', 'user').prefetch_related('attachments')
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    parser_classes = (JSONParser, MultiPartParser)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AttachmentViewSet(viewsets.ModelViewSet):
    queryset = Attachment.objects.all().select_related('task', 'uploaded_by')
    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    parser_classes = (JSONParser, MultiPartParser)

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)