from django.db import models
from users.models import CustomUser
# Create your models here.
class Task(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateField(blank=True, null=True)
    assigned_to = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        related_name='assigned_tasks',
        blank=True, null=True
    )

    # parent-child task relationship (for sub-tasks)
    parent_task = models.ForeignKey(
        'self', on_delete=models.CASCADE, 
        related_name='subtasks',
        blank=True, null=True
    )
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class TaskReopenRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    task = models.ForeignKey(
        'Task', on_delete=models.CASCADE, related_name='reopen'
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='reopen'
    )
    message =models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

class TaskComment(models.Model):
    task = models.ForeignKey(
        'Task', on_delete=models.CASCADE, related_name='comments'
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.task}"
    
class Attachment(models.Model):
    task = models.ForeignKey(
        'Task', on_delete=models.CASCADE, related_name='attachments'
    )
    uploaded_by = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='attachments'
    )
    file = models.FileField(upload_to='task_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Attachment for {self.task.title} by {self.uploaded_by}"
    
class TaskActivityLog(models.Model):
    ACTION_CHOICES = (
        ('created', 'Task Created'),
        ('updated', 'Task Updated'),
        ('status_changed', 'Status Changed'),
        ('assigned', 'Task Assigned'),
        ('comment_added', 'Comment Added'),
        ('attachment_added', 'Attachment Added'),
        ('deleted', 'Task Deleted'),
    )

    task = models.ForeignKey(
        'Task', on_delete=models.CASCADE, related_name='activity_logs'
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='task_logs'
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_action_display()} by {self.user} on {self.task.title}"
