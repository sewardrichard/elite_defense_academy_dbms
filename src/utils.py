import os
import re
from datetime import datetime

def load_env_from_file():
    """Load key=value pairs from project root .env if present."""
    # Look for .env in the project root (3 levels up from src/utils.py if src is in root, wait, src is in root)
    # Based on user info: c:\Users\sewar\repos\elite_defense_academy_dbms\src
    # .env is in c:\Users\sewar\repos\elite_defense_academy_dbms\.env
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    
    if not os.path.isfile(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            # Remove quotes if present
            if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                v = v[1:-1]
            
            if k and v and k not in os.environ:
                os.environ[k] = v

def validate_date(date_text):
    """Validate date format YYYY-MM-DD."""
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_email(email):
    """Simple regex validation for email."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_score(score):
    """Validate score is between 0 and 100."""
    try:
        s = float(score)
        return 0 <= s <= 100
    except ValueError:
        return False

def get_user_input(prompt, validator=None, required=True):
    """
    Get input from user with validation and exit option.
    Returns None if user types 'q' or 'back'.
    """
    while True:
        value = input(f"{prompt} (or 'q' to cancel): ").strip()
        
        if value.lower() in ['q', 'back', 'quit']:
            return None
            
        if not value and required:
            print("Error: This field is required.")
            continue
            
        if not value and not required:
            return ""

        if validator:
            if validator(value):
                return value
            else:
                print("Error: Invalid format. Please try again.")
        else:
            return value
