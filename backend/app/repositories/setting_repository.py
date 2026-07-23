from typing import List, Optional
from app.extensions import db
from app.models.setting import SystemSetting, UserPreference

class SettingRepository:
    """Encapsulates transactional operations on application configurations and user preferences."""

    def get_system_setting(self, key: str) -> Optional[SystemSetting]:
        return db.session.query(SystemSetting).filter(SystemSetting.key == key).first()

    def list_system_settings(self, category: Optional[str] = None) -> List[SystemSetting]:
        query = db.session.query(SystemSetting)
        if category:
            query = query.filter(SystemSetting.category == category)
        return query.all()

    def set_system_setting(self, key: str, value: str, description: Optional[str] = None, category: str = "SYSTEM") -> SystemSetting:
        setting = self.get_system_setting(key)
        if setting:
            setting.value = value
            if description:
                setting.description = description
        else:
            setting = SystemSetting(key=key, value=value, description=description, category=category)
            db.session.add(setting)
        db.session.flush()
        return setting

    def get_user_preference(self, user_id: str) -> Optional[UserPreference]:
        return db.session.query(UserPreference).filter(UserPreference.user_id == user_id).first()

    def set_user_preference(self, user_id: str, preferences_json: dict) -> UserPreference:
        pref = self.get_user_preference(user_id)
        if pref:
            pref.preferences_json = preferences_json
        else:
            pref = UserPreference(user_id=user_id, preferences_json=preferences_json)
            db.session.add(pref)
        db.session.flush()
        return pref

    def save(self):
        db.session.commit()
