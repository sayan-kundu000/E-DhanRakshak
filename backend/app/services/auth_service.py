from datetime import datetime, timezone, timedelta
from flask_jwt_extended import create_access_token, create_refresh_token

from app.extensions import bcrypt
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.middleware.error_handler import ValidationError, AuthError, ResourceNotFoundError

class AuthService:
    """Orchestrates business operations for signups, logins, and profiles management."""

    def __init__(self, user_repository: UserRepository = None):
        self.user_repo = user_repository or UserRepository()

    def register_user(self, data: dict, ip_address: str) -> User:
        """Processes registrations, enforcing duplicate checks and password encryption."""
        email = data["email"].strip().lower()
        if self.user_repo.get_by_email(email):
            raise ValidationError("Email address is already registered.")

        hashed = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
        
        user = User(
            email=email,
            password_hash=hashed,
            full_name=data["full_name"].strip(),
            role=data["role"],
            is_active=True
        )
        
        saved_user = self.user_repo.create(user)
        self.user_repo.save(saved_user)
        
        # Log write audit event
        self.user_repo.add_audit_log(
            user_id=saved_user.id, 
            action="USER_REGISTRATION", 
            ip_address=ip_address,
            payload={"email": email, "role": saved_user.role}
        )
        
        return saved_user

    def login_user(self, credentials: dict, ip_address: str) -> tuple:
        """Handles authentication credentials verification, locks, and logs history details."""
        email = credentials["email"].strip().lower()
        user = self.user_repo.get_by_email(email)
        
        if not user:
            # Prevent email enumeration by adding dummy verification timing
            bcrypt.generate_password_hash("dummy_password")
            raise AuthError("Invalid credentials.")
            
        # Check lockout state
        if user.is_locked:
            time_left = int((user.locked_until - datetime.now(timezone.utc)).total_seconds() / 60)
            raise AuthError(f"Account locked. Please try again in {time_left} minutes.")

        # Check credentials
        if not bcrypt.check_password_hash(user.password_hash, credentials["password"]):
            # Increment failed logins counter
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
                self.user_repo.add_audit_log(
                    user_id=user.id,
                    action="ACCOUNT_LOCKED",
                    ip_address=ip_address,
                    payload={"attempts": user.failed_login_attempts}
                )
            self.user_repo.save(user)
            self.user_repo.add_audit_log(
                user_id=user.id,
                action="LOGIN_FAILURE",
                ip_address=ip_address
            )
            raise AuthError("Invalid credentials.")

        if not user.is_active:
            raise AuthError("Account has been deactivated. Contact an administrator.")

        # Authentication success: reset tracker indices
        user.failed_login_attempts = 0
        user.locked_until = None
        self.user_repo.save(user)
        
        # Generate JWT tokens including role details inside claims dictionaries
        access_token = create_access_token(
            identity=str(user.id), 
            additional_claims={"role": user.role}
        )
        refresh_token = create_refresh_token(identity=str(user.id))
        
        self.user_repo.add_audit_log(
            user_id=user.id,
            action="LOGIN_SUCCESS",
            ip_address=ip_address
        )
        
        return access_token, refresh_token, user

    def get_profile(self, user_id: str) -> User:
        """Fetches active user details."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError("User profile could not be found.")
        return user

    def update_profile(self, user_id: str, data: dict, ip_address: str) -> User:
        """Saves profile changes."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError("User profile could not be found.")
            
        user.full_name = data["full_name"].strip()
        self.user_repo.save(user)
        
        self.user_repo.add_audit_log(
            user_id=user.id,
            action="UPDATE_PROFILE",
            ip_address=ip_address
        )
        return user

    def change_password(self, user_id: str, data: dict, ip_address: str) -> User:
        """Updates account passwords checking current matching strings."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError("User profile could not be found.")
            
        if not bcrypt.check_password_hash(user.password_hash, data["current_password"]):
            raise ValidationError("Incorrect current password configuration.")
            
        user.password_hash = bcrypt.generate_password_hash(data["new_password"]).decode("utf-8")
        self.user_repo.save(user)
        
        self.user_repo.add_audit_log(
            user_id=user.id,
            action="CHANGE_PASSWORD",
            ip_address=ip_address
        )
        return user

    def toggle_user_activation(self, target_user_id: str, is_active: bool, admin_user_id: str, ip_address: str) -> User:
        """Enables administrators to lock or unlock system access levels."""
        user = self.user_repo.get_by_id(target_user_id)
        if not user:
            raise ResourceNotFoundError("Target user could not be found.")
            
        # Prevent self-deactivation loops
        if target_user_id == admin_user_id and not is_active:
            raise ValidationError("Administrators cannot deactivate their own profiles.")
            
        user.is_active = is_active
        self.user_repo.save(user)
        
        action_name = "DEACTIVATE_USER" if not is_active else "ACTIVATE_USER"
        self.user_repo.add_audit_log(
            user_id=admin_user_id,
            action=action_name,
            ip_address=ip_address,
            payload={"target_user_id": target_user_id}
        )
        return user
