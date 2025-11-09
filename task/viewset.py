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
from .models import Task,TaskComment,Attachment,TaskReopenRequest
from .serializers import TaskSerializer,CommentSerializer,AttachmentSerializer,TaskReopenRequestSerializer,\
    TaskActivityLogSerializer
from rest_framework.response import Response
from rest_framework import status
from users.email import send_task_assigned_email,send_task_completed_email,send_task_reopen_request_email,\
    send_reopen_request_status_email

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
        perm = self.request.query_params.get('perm')
        created_by = self.request.query_params.get('created_by')
        # user = self.request.query_params.get('user')
        # if user:
        #     queryset = queryset.filter(user=user)
        if status:
            queryset = queryset.filter(status=status)
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        if created_by:
            queryset = queryset.filter(created_by_id=created_by)
        if perm:
            queryset = super().get_queryset()
            if self.request.user.is_task_create:
                queryset = queryset.filter(created_by=self.request.user.id)
            elif self.request.user.is_task_recive:
                queryset = queryset.filter(assigned_to=self.request.user.id)
            else:
                pass
        

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
        send_task_assigned_email(task)
        log_task_activity(task, self.request.user, 'created', f"Task '{task.title}' created.")

    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        user = request.user
        self_tasks=''
        # --- Self Stats ---
        if user.is_superuser:
            self_tasks = Task.objects.all()
        else:
            self_tasks = Task.objects.filter(assigned_to=user)
        self_stats = {
            "total": self_tasks.count(),
            "pending": self_tasks.filter(status='pending').count(),
            "in_progress": self_tasks.filter(status='in_progress').count(),
            "completed": self_tasks.filter(status='completed').count(),
        }
        data = {
            "self": self_stats
        }

        return Response(data)

    def perform_update(self, serializer):
        old_task = self.get_object()
        new_task = serializer.save()
        if new_task.status=='completed':
            send_task_completed_email(new_task)
        # Detect changes
        changes = []
        if old_task.status != new_task.status:
            changes.append(f"{self.request.user.first_name} {self.request.user.last_name} change the status from '{old_task.status}' to '{new_task.status}'.")
            log_task_activity(new_task, self.request.user, 'status_changed', changes[-1])

        if old_task.assigned_to != new_task.assigned_to:
            old_name = old_task.assigned_to.get_full_name() if old_task.assigned_to else 'None'
            new_name = new_task.assigned_to.get_full_name() if new_task.assigned_to else 'None'
            changes.append(f"Assigned changed from '{old_name}' to '{new_name}'.")
            log_task_activity(new_task, self.request.user, 'assigned', changes[-1])

        if old_task.priority != new_task.priority:
            changes.append(f"{self.request.user.first_name} {self.request.user.last_name} changed Priority from '{old_task.priority}' to '{new_task.priority}'.")
            log_task_activity(new_task, self.request.user, 'priority', changes[-1])

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
                log_message=f'{self.request.user.first_name} {self.request.user.last_name} makes a comment'
                log_task_activity(task, self.request.user, 'priority', log_message)
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
                log_message=f'{self.request.user.first_name} {self.request.user.last_name} Upload a Attachment'
                log_task_activity(task, self.request.user, 'priority', log_message)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['get', 'post','patch'], url_path='reopen')
    def reopen(self, request, pk=None):
        task = self.get_object()

        if request.method == 'GET':
            attachments = task.reopen.all()
            serializer = TaskReopenRequestSerializer(attachments, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = TaskReopenRequestSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                obj=serializer.save(user=request.user, task=task)
                send_task_reopen_request_email(obj)
                log_message=f'{self.request.user.first_name} {self.request.user.last_name} request to reopen task'
                log_task_activity(task, self.request.user, 'reopen', log_message)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'PATCH':
            reopen_id = request.data.get('id')
            new_status = request.data.get('status')

            if not reopen_id or not new_status:
                return Response(
                    {"error": "Both 'id' and 'status' are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                reopen_request = task.reopen.get(id=reopen_id)
            except TaskReopenRequest.DoesNotExist:
                return Response({"error": "Reopen request not found."}, status=status.HTTP_404_NOT_FOUND)

            reopen_request.status = new_status
            reopen_request.save()
            log_message = f"{request.user.first_name} {request.user.last_name} changed reopen request status to {new_status}"
            log_task_activity(task, request.user, 'reopen_status', log_message)

            if new_status == 'accepted':
                task.status = 'in_progress'  # or 'pending', depending on your logic
                task.save()

                log_message = f"Task '{task.title}' reopened and moved to {task.status}"
                log_task_activity(task, request.user, 'task_status_update', log_message)
            send_reopen_request_status_email(reopen_request)
            serializer = TaskReopenRequestSerializer(reopen_request)
            return Response(serializer.data, status=status.HTTP_200_OK)

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