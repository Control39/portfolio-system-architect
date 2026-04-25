"""Helpers stub for pytest collection."""

def validate_email(email):
    return "@" in email # stub

def sanitize_filename(filename):
    return "".join(c for c in filename if c.isalnum() or c in ".-_ ") # stub

def calculate_skill_progress(current, total):
    return min(100, max(0, (current / total * 100))) # stub

def get_competency_level_name(level):
    levels = {1: "Новичок", 3: "Средний", 5: "Эксперт"}
    return levels.get(level, "Не определен") # stub

def format_date(date_str):
    return date_str # stub

def convert_bytes_to_human_readable(bytes_size):
    return f"{bytes_size} B" # stub

def load_json_file(filename):
    return {"stub": True} # stub

def save_json_file(filename, data):
    return True # stub

def create_directory_if_not_exists(dir_path):
    return True # stub

def get_file_size(filename):
    return 1024 # stub

# Export all
__all__ = ["calculate_skill_progress", "convert_bytes_to_human_readable", "create_directory_if_not_exists", "format_date", "get_competency_level_name", "get_file_size", "load_json_file", "sanitize_filename", "save_json_file", "validate_email"]


