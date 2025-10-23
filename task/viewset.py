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

from rest_framework import viewsets, permissions
from .models import Task
from .serializers import TaskSerializer
from rest_framework.response import Response
from rest_framework import status

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    parser_classes = (JSONParser, MultiPartParser)

    # def get_queryset(self):
    #     user = self.request.user
    #     # Superadmin & Superuser → can see all tasks
    #     if user.role in ['superadmin', 'superuser']:
    #         return Task.objects.all()
    #     # Normal user → can see only their tasks
    #     return Task.objects.filter(assigned_to=user)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(created_by=user)