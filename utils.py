import logging
from datetime import datetime
import json
import os

def log_error(message):
    logging.error(f"{datetime.now()}: {message}")

def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def is_overdue(task):
    if task.get("completed"):
        return False
    due_date_str = task.get("due_date")
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
            return datetime.now() > due_date
        except ValueError:
            return False
    return False

# def load_tasks(): 
#     if os.path.exists("tasks.json"):
#         try:
#             with open("tasks.json", "r") as f:
#                 return json.load(f)
#         except json.JSONDecodeError as e:
#             log_error(f"JSON decode error: {e}")
#             return []
#         except Exception as e:
#             log_error(f"Unexpected error loading tasks: {e}")
#             return []
#     return []

# def save_tasks(tasks):
#     with open("tasks.json", "w") as f:
#         json.dump(tasks, f, indent=4)    