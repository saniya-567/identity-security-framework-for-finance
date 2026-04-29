from .models import AuditLog

def log_action(user, action):
    username = user.username if user else "Unknown"

    AuditLog.objects.create(
        user=username,
        action=action
    )

    