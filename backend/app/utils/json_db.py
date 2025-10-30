# JSON Database Operations
import json
import os
from typing import Dict, Any, Optional

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
        # Reload data to ensure we have latest state
        self.data = self._load_data()

        if collection not in self.data:
            self.data[collection] = {}

        self.data[collection][item_id] = data
        self.save()
        return data

    def find_by_id(self, collection: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Find item by ID in collection"""
        # Reload data to ensure we have latest state
        self.data = self._load_data()
        return self.data.get(collection, {}).get(item_id)

    def find_all(self, collection: str) -> Dict[str, Any]:
        """Get all items in collection"""
        # Reload data to ensure we have latest state
        self.data = self._load_data()
        return self.data.get(collection, {})

    def update(self, collection: str, item_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing item"""
        # Reload data to ensure we have latest state
        self.data = self._load_data()

        if collection in self.data and item_id in self.data[collection]:
            self.data[collection][item_id].update(updates)
            self.save()
            return self.data[collection][item_id]
        return None

    def delete(self, collection: str, item_id: str) -> bool:
        """Delete item from collection"""
        # Reload data to ensure we have latest state
        self.data = self._load_data()

        if collection in self.data and item_id in self.data[collection]:
            del self.data[collection][item_id]
            self.save()
            return True
        return False

    def find_by_field(self, collection: str, field: str, value: Any) -> Optional[Dict[str, Any]]:
        """Find first item where field equals value"""
        # Reload data to ensure we have latest state
        self.data = self._load_data()

        items = self.data.get(collection, {})
        for item_id, item_data in items.items():
            if item_data.get(field) == value:
                return item_data
        return None

    def list_by_field(self, collection: str, field: str, value: Any) -> list:
        """List all items where field equals value"""
        # Reload data to ensure we have latest state
        self.data = self._load_data()

        items = self.data.get(collection, {})
        results = []
        for item_id, item_data in items.items():
            if item_data.get(field) == value:
                results.append(item_data)
        return results


# Database instances (singletons)
users_db = JSONDatabase('data/users.json')
email_tokens_db = JSONDatabase('data/email_tokens.json')
calendars_db = JSONDatabase('data/calendars.json')
tasks_db = JSONDatabase('data/tasks.json')