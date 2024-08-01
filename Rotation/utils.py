import json
from django.conf import settings
from pathlib import Path
from django.db import connections

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / 'config.json'

def get_database_location():
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config.get('database_location', 'db.sqlite3')
    except FileNotFoundError:
        return 'db.sqlite3'  # Default value if file doesn't exist

def update_database_location(new_location):
    print("Updating database location")
    current_location = get_database_location()
    if new_location == current_location:
        return True

    try:
        with open(CONFIG_FILE, 'r+') as f:
            config = json.load(f)
            config['database_location'] = new_location
            f.seek(0)
            json.dump(config, f, indent=4)
            f.truncate()
        
        # Update the database configuration
        connections.databases['default']['NAME'] = str(settings.BASE_DIR / new_location)
        return True
    except Exception as e:
        print(f"Error updating config file: {e}")
        return False
