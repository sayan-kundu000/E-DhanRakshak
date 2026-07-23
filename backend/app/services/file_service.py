import os
import hashlib
import uuid
import logging
from typing import Tuple, List
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask import current_app
from app.models.file_attachment import FileAttachment
from app.repositories.file_repository import FileRepository
from app.middleware.error_handler import ValidationError, ResourceNotFoundError, StorageError

logger = logging.getLogger("app.security")

class FileService:
    """Orchestrates secure file storage, metadata saving, checksum validation, and downloads."""

    def __init__(self, file_repository: FileRepository = None):
        self.file_repo = file_repository or FileRepository()

    def _compute_checksum(self, file_bytes: bytes) -> str:
        """Calculates MD5 hash for duplicate upload checking."""
        return hashlib.md5(file_bytes).hexdigest()

    def upload_file(self, file: FileStorage, owner_id: str) -> FileAttachment:
        # Validate file presence
        if not file or not file.filename:
            raise ValidationError("No file payload provided.")

        # Read file bytes to check size and checksum
        file_bytes = file.read()
        file_size = len(file_bytes)
        
        # Reset pointer for possible future operations
        file.seek(0)

        # Check file size boundaries (MAX content length check)
        max_size = current_app.config.get("MAX_CONTENT_LENGTH", 5 * 1024 * 1024)
        if file_size > max_size:
            raise ValidationError(f"File size exceeds maximum permitted limit of {max_size / (1024 * 1024):.1f}MB.")

        # Validate filename and path traversal prevention
        orig_name = secure_filename(file.filename)
        if not orig_name or "." not in orig_name:
            raise ValidationError("Invalid filename properties.")

        ext = orig_name.rsplit(".", 1)[1].lower()
        allowed_exts = current_app.config.get("ALLOWED_EXTENSIONS", {"png", "jpg", "jpeg", "pdf", "doc", "docx"})
        if ext not in allowed_exts:
            raise ValidationError(f"File extension '.{ext}' is not permitted.")

        # Check duplicate uploads using checksum
        checksum = self._compute_checksum(file_bytes)
        existing = self.file_repo.get_by_checksum(checksum)
        if existing:
            # Duplicate upload detected; return existing metadata to conserve storage!
            logger.info(f"Duplicate upload detected. Mapping metadata referencing stored file: {existing.stored_name}")
            return existing

        # Generate a secure unique stored filename
        stored_name = f"{uuid.uuid4().hex}.{ext}"
        storage_path = os.path.join(current_app.config["UPLOAD_FOLDER"], stored_name)

        try:
            # Write file to local disk
            with open(storage_path, "wb") as f:
                f.write(file_bytes)
        except Exception as e:
            logger.error(f"Failed to write file to storage: {str(e)}", exc_info=True)
            raise StorageError("Could not write file to storage system.")

        # Save metadata record
        attachment = FileAttachment(
            original_name=orig_name,
            stored_name=stored_name,
            extension=ext,
            content_type=file.content_type or "application/octet-stream",
            file_size=file_size,
            owner_id=owner_id,
            checksum=checksum,
            storage_path=storage_path
        )

        saved = self.file_repo.create(attachment)
        self.file_repo.save()
        
        logger.info(f"File uploaded successfully by User {owner_id}. Stored as {stored_name}")
        return saved

    def get_file_metadata(self, file_id: str) -> FileAttachment:
        file_record = self.file_repo.get_by_id(file_id)
        if not file_record:
            raise ResourceNotFoundError("File record not found.")
        return file_record

    def get_file_by_name(self, stored_name: str) -> FileAttachment:
        file_record = self.file_repo.get_by_stored_name(stored_name)
        if not file_record:
            raise ResourceNotFoundError("File record not found.")
        return file_record

    def delete_file(self, file_id: str, user_id: str, user_role: str) -> None:
        file_record = self.get_file_metadata(file_id)

        # Access check: Only owner, STAFF, or ADMIN can delete
        if user_role not in ["ADMINISTRATOR", "STAFF"] and str(file_record.owner_id) != str(user_id):
            raise ValidationError("You do not possess deletion permissions for this file attachment.")

        # Mark as deleted in database
        file_record.is_deleted = True
        self.file_repo.save()

        # Delete from local disk
        if os.path.exists(file_record.storage_path):
            try:
                os.remove(file_record.storage_path)
            except Exception as e:
                logger.error(f"Failed to remove file from disk: {file_record.storage_path}. Error: {str(e)}")

        logger.info(f"File {file_record.stored_name} deleted by User {user_id}")
