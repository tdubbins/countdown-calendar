# JSON Database Operations
import json
import os
from typing import Dict, Any, Optional
from app.utils.constants import StoragePaths

class JSONDatabase:
    """JSON file-based database operations"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Load data from JSON file"""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r') as file:
                    return json.load(file)
            else:
                return {}
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Warning: {self.file_path} is corrupted or missing, creating new file")
            return {}
    
    def save(self) -> None:
        """Save data to JSON file"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        
        with open(self.file_path, 'w') as file:
            json.dump(self.data, file, indent=2)
    
    def create(self, collection: str, item_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new item in collection"""
        self.data = self._load_data()

        if collection not in self.data:
            self.data[collection] = {}

        self.data[collection][item_id] = data
        self.save()
        return data

    def find_by_id(self, collection: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Find item by ID in collection"""
        self.data = self._load_data()
        return self.data.get(collection, {}).get(item_id)

    def find_all(self, collection: str) -> Dict[str, Any]:
        """Get all items in collection"""
        self.data = self._load_data()
        return self.data.get(collection, {})

    def update(self, collection: str, item_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing item"""
        self.data = self._load_data()

        if collection in self.data and item_id in self.data[collection]:
            self.data[collection][item_id].update(updates)
            self.save()
            return self.data[collection][item_id]
        return None

    def delete(self, collection: str, item_id: str) -> bool:
        """Delete item from collection"""
        self.data = self._load_data()

        if collection in self.data and item_id in self.data[collection]:
            del self.data[collection][item_id]
            self.save()
            return True
        return False

    def find_by_field(self, collection: str, field: str, value: Any) -> Optional[Dict[str, Any]]:
        """Find first item where field equals value"""
        self.data = self._load_data()

        items = self.data.get(collection, {})
        for item_id, item_data in items.items():
            if item_data.get(field) == value:
                return item_data
        return None

    def list_by_field(self, collection: str, field: str, value: Any) -> list:
        """List all items where field equals value"""
        self.data = self._load_data()

        items = self.data.get(collection, {})
        results = []
        for item_id, item_data in items.items():
            if item_data.get(field) == value:
                results.append(item_data)
        return results


# Calendar-specific file operations
class CalendarDatabase:
    """Per-calendar folder-based database operations"""

    CALENDARS_DIR = StoragePaths.CALENDARS_DIR

    @classmethod
    def read_calendar_meta(cls, calendar_id: str) -> Optional[Dict[str, Any]]:
        """Read calendar meta.json file"""
        try:
            meta_path = os.path.join(cls.CALENDARS_DIR, calendar_id, 'meta.json')
            if os.path.exists(meta_path):
                with open(meta_path, 'r') as f:
                    return json.load(f)
            return None
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading calendar {calendar_id}: {e}")
            return None

    @classmethod
    def write_calendar_meta(cls, calendar_id: str, data: Dict[str, Any]) -> bool:
        """Write calendar meta.json file"""
        try:
            calendar_dir = os.path.join(cls.CALENDARS_DIR, calendar_id)
            os.makedirs(calendar_dir, exist_ok=True)

            meta_path = os.path.join(calendar_dir, 'meta.json')
            with open(meta_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error writing calendar {calendar_id}: {e}")
            return False

    @classmethod
    def update_calendar_meta(cls, calendar_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Partially update calendar meta.json"""
        meta = cls.read_calendar_meta(calendar_id)
        if meta:
            meta.update(updates)
            if cls.write_calendar_meta(calendar_id, meta):
                return meta
        return None

    @classmethod
    def delete_calendar_folder(cls, calendar_id: str) -> bool:
        """Delete entire calendar folder"""
        try:
            import shutil
            calendar_dir = os.path.join(cls.CALENDARS_DIR, calendar_id)
            if os.path.exists(calendar_dir):
                shutil.rmtree(calendar_dir)
                return True
            return False
        except Exception as e:
            print(f"Error deleting calendar {calendar_id}: {e}")
            return False

    @classmethod
    def calendar_exists(cls, calendar_id: str) -> bool:
        """Check if calendar folder exists"""
        calendar_dir = os.path.join(cls.CALENDARS_DIR, calendar_id)
        return os.path.exists(calendar_dir) and os.path.isdir(calendar_dir)

    @classmethod
    def create_calendar_structure(cls, calendar_id: str) -> bool:
        """Create calendar folder structure (folder, meta.json, subfolders)"""
        try:
            calendar_dir = os.path.join(cls.CALENDARS_DIR, calendar_id)
            os.makedirs(calendar_dir, exist_ok=True)
            os.makedirs(os.path.join(calendar_dir, 'videos'), exist_ok=True)
            os.makedirs(os.path.join(calendar_dir, 'thumbnails'), exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating calendar structure {calendar_id}: {e}")
            return False


# User operations helper functions
def get_user_calendar_ids(user_id: str) -> list:
    """Get list of calendar IDs for a user"""
    user = users_db.find_by_id('users', user_id)
    if user:
        return user.get('calendar_ids', [])
    return []


def add_calendar_to_user(user_id: str, calendar_id: str) -> bool:
    """Add calendar ID to user's calendar_ids array"""
    calendar_ids = get_user_calendar_ids(user_id)
    if calendar_id not in calendar_ids:
        calendar_ids.append(calendar_id)
        return users_db.update('users', user_id, {'calendar_ids': calendar_ids}) is not None
    return True  # Already exists


def remove_calendar_from_user(user_id: str, calendar_id: str) -> bool:
    """Remove calendar ID from user's calendar_ids array"""
    calendar_ids = get_user_calendar_ids(user_id)
    if calendar_id in calendar_ids:
        calendar_ids.remove(calendar_id)
        return users_db.update('users', user_id, {'calendar_ids': calendar_ids}) is not None
    return True  # Already removed


# Database instances (singletons)
users_db = JSONDatabase('data/users.json')
email_tokens_db = JSONDatabase('data/email_tokens.json')
tasks_db = JSONDatabase('data/tasks.json')

# Calendar database (new per-calendar structure)
calendars_db = CalendarDatabase()