from .models import TaskActivityLog

def log_task_activity(task, user, action, message=""):
    TaskActivityLog.objects.create(
        task=task,
        user=user,
        action=action,
        message=message
    )