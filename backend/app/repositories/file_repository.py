from typing import Optional, List, Tuple
from app.extensions import db
from app.models.file_attachment import FileAttachment

class FileRepository:
    """Encapsulates CRUD operations on file attachments and uploads records."""

    def create(self, file_attachment: FileAttachment) -> FileAttachment:
        db.session.add(file_attachment)
        db.session.flush()
        return file_attachment

    def get_by_id(self, file_id: str) -> Optional[FileAttachment]:
        return db.session.query(FileAttachment).filter(
            FileAttachment.id == file_id,
            FileAttachment.is_deleted == False
        ).first()

    def get_by_stored_name(self, stored_name: str) -> Optional[FileAttachment]:
        return db.session.query(FileAttachment).filter(
            FileAttachment.stored_name == stored_name,
            FileAttachment.is_deleted == False
        ).first()

    def get_by_checksum(self, checksum: str) -> Optional[FileAttachment]:
        """Finds active duplicate upload using file MD5 checksum values."""
        return db.session.query(FileAttachment).filter(
            FileAttachment.checksum == checksum,
            FileAttachment.is_deleted == False
        ).first()

    def list_files(self, owner_id: Optional[str] = None, page: int = 1, limit: int = 10) -> Tuple[List[FileAttachment], int]:
        query = db.session.query(FileAttachment).filter(FileAttachment.is_deleted == False)
        if owner_id:
            query = query.filter(FileAttachment.owner_id == owner_id)
        
        total = query.count()
        records = query.order_by(FileAttachment.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
        return records, total

    def save(self):
        db.session.commit()
