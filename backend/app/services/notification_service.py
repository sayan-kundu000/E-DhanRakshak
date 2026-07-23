import logging
from typing import List, Tuple, Optional
from app.models.notification import Notification
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository
from app.middleware.error_handler import ResourceNotFoundError

logger = logging.getLogger("app.security")

class NotificationService:
    """Orchestrates system alerts dispatch, emailing, and mock SMS alerts logging."""

    def __init__(self, notification_repository: NotificationRepository = None, user_repository: UserRepository = None):
        self.notification_repo = notification_repository or NotificationRepository()
        self.user_repo = user_repository or UserRepository()

    def send_notification(self, user_id: str, title: str, message: str, notification_type: str = "IN_APP", priority: str = "MEDIUM") -> Notification:
        # Verify user exists
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError("Recipient user not found.")

        # Create model
        notification = Notification(
            user_id=user_id,
            title=title.strip(),
            message=message.strip(),
            type=notification_type,
            priority=priority,
            is_read=False
        )

        saved = self.notification_repo.create(notification)
        self.notification_repo.save()

        # Handle Mock SMS / Email notification actions
        if notification_type == "EMAIL":
            logger.info(f"EMAIL DISPATCHED to {user.email}: Title: {title}")
        elif notification_type == "SMS":
            logger.info(f"SMS (MOCKED) DISPATCHED to user {user.full_name}: Title: {title}")
        else:
            logger.info(f"IN_APP Alert generated for User: {user.email}")

        return saved

    def list_notifications(self, user_id: str, is_read: Optional[bool] = None, page: int = 1, limit: int = 10) -> Tuple[List[Notification], int]:
        return self.notification_repo.list_by_user(user_id, is_read, page, limit)

    def mark_as_read(self, notification_id: str, user_id: str) -> Notification:
        notification = self.notification_repo.get_by_id(notification_id)
        if not notification:
            raise ResourceNotFoundError("Notification alert not found.")
        if str(notification.user_id) != str(user_id):
            raise ResourceNotFoundError("Notification alert not found.")  # Avoid enumerating security errors
        
        notification.is_read = True
        self.notification_repo.save()
        return notification

    def mark_all_read(self, user_id: str) -> int:
        count = self.notification_repo.mark_all_read(user_id)
        self.notification_repo.save()
        return count
