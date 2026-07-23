import json
from typing import List, Optional
from app.models.setting import SystemSetting, UserPreference
from app.repositories.setting_repository import SettingRepository
from app.middleware.error_handler import ResourceNotFoundError

class SettingService:
    """Orchestrates system-level variables modifications and user preference setups."""

    def __init__(self, setting_repository: SettingRepository = None):
        self.setting_repo = setting_repository or SettingRepository()

    def get_system_setting(self, key: str) -> SystemSetting:
        setting = self.setting_repo.get_system_setting(key)
        if not setting:
            raise ResourceNotFoundError(f"Configuration key '{key}' not found.")
        return setting

    def list_system_settings(self, category: Optional[str] = None) -> List[SystemSetting]:
        return self.setting_repo.list_system_settings(category)

    def set_system_setting(self, key: str, value: str, description: Optional[str] = None, category: str = "SYSTEM") -> SystemSetting:
        setting = self.setting_repo.set_system_setting(key, value, description, category)
        self.setting_repo.save()
        return setting

    def get_user_preference(self, user_id: str) -> UserPreference:
        pref = self.setting_repo.get_user_preference(user_id)
        if not pref:
            # Return default preferences if not customized yet
            default_pref = {
                "dark_mode": False,
                "email_notifications": True,
                "sms_notifications": False,
                "in_app_notifications": True
            }
            pref = self.setting_repo.set_user_preference(user_id, default_pref)
            self.setting_repo.save()
        return pref

    def set_user_preference(self, user_id: str, preferences_json: dict) -> UserPreference:
        pref = self.setting_repo.set_user_preference(user_id, preferences_json)
        self.setting_repo.save()
        return pref
