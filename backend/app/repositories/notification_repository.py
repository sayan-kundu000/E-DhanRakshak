from typing import List, Tuple, Optional
from app.extensions import db
from app.models.notification import Notification

class NotificationRepository:
    """Encapsulates database actions for user alerts and system notifications."""

    def create(self, notification: Notification) -> Notification:
        db.session.add(notification)
        db.session.flush()
        return notification

    def get_by_id(self, notification_id: str) -> Optional[Notification]:
        return db.session.query(Notification).filter(Notification.id == notification_id).first()

    def list_by_user(
        self, 
        user_id: str, 
        is_read: Optional[bool] = None, 
        page: int = 1, 
        limit: int = 10
    ) -> Tuple[List[Notification], int]:
        query = db.session.query(Notification).filter(Notification.user_id == user_id)
        
        if is_read is not None:
            query = query.filter(Notification.is_read == is_read)
            
        total = query.count()
        records = query.order_by(Notification.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
        return records, total

    def mark_all_read(self, user_id: str) -> int:
        updated = db.session.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({Notification.is_read: True}, synchronize_session=False)
        return updated

    def save(self):
        db.session.commit()
