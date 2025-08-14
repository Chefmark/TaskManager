from flask import Flask,flash, render_template, request, redirect, url_for
import json
import os
from datetime import datetime
from key import flashkey as fkey
import uuid
import logging

app = Flask(__name__)
app.secret_key = fkey
logging.basicConfig(
    filename='error.log',
    level =logging.ERROR,
    format='%(asctime)s:%(levelname)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Global definitions
def load_tasks(): 
    if os.path.exists("tasks.json"):
        try:
            with open("tasks.json", "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            log_error(f"JSON decode error: {e}")
            return []
        except Exception as e:
            log_error(f"Unexpected error loading tasks: {e}")
            return []
    return []

def save_tasks(tasks):
    with open("tasks.json", "w") as f:
        json.dump(tasks, f, indent=4)

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

def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def log_error(message):
    logging.error(f"{datetime.now()}: {message}")

@app.route("/")
def index():
    sort_by = request.args.get("sort", "default")
    filter_tag = request.args.get("tag")
    search_query = request.args.get("search", "").lower()
    tasks = load_tasks()

    if filter_tag:
        tasks = [task for task in tasks if filter_tag in task.get("tags",[])]

    if search_query:
        tasks = [
            task for task in tasks
            if search_query in task.get("title", "").lower() or search_query in task.get("description", "").lower()
        ]
    if sort_by == "due":
        tasks.sort(key=lambda x: x.get("due_date") or "")
    elif sort_by == "title":
        tasks.sort(key=lambda x: x.get("title","").lower())
    elif sort_by == "status":
        tasks.sort(key=lambda x: x.get("completed", False))
    elif sort_by == "priority": 
        priority_order = {"High": 0, "Medium":1, "Low":2}
        tasks.sort(key=lambda x: priority_order.get(x.get("priority", "Medium")))
    
    for task in tasks:
        task["is_overdue"] = is_overdue(task)
    
    return render_template("index.html", tasks=tasks, filter_tag=filter_tag, search_query=search_query)

@app.route("/add", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        try:
            title = request.form["title"]
            description = request.form["description"]
            due_date = request.form["due_date"]
            tags = request.form["tags"].split(",") if request.form["tags"] else []
            priority = request.form["priority"]
            if not title:
                flash("Title is required!", "error")
                return redirect(url_for("add_task"))
            if due_date:
                try:
                    datetime.strptime(due_date, "%Y-%m-%d")
                except ValueError:
                    flash("Invalid date format. Use YYYY-MM-DD.", "error")
                    return redirect(url_for("add_task"))
            if priority not in ["High", "Medium", "Low"]:
                flash("Invalid priority. Choose High, Medium, or Low.", "error")
                return redirect(url_for("add_task"))

            task = {
                "id": str(uuid.uuid4()),
                "title": title,
                "description": description,
                "due_date": due_date,
                "completed": False,
                "tags": tags,
                "priority": priority
            }
            tasks = load_tasks()
            tasks.append(task)
            save_tasks(tasks)
            flash("Task added successfully!", "success")
            return redirect(url_for("index"))
        except Exception as e:
            log_error(f"Error adding task: {e}")
            flash("An error occurred while adding the task.", "error")
            return redirect(url_for("add_task"))
    return render_template("add_task.html")

@app.route("/edit/<task_id>", methods =["GET", "POST"])
def edit_task(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t["id"]==task_id), None)
    if not task:
        log_error(f"Task with ID {task_id} not found for editing.")
        flash("Task not found.", "error")
        return "Task not found", 404

    if request.method == "POST":
        try:
            task["title"] = request.form["title"]
            task["description"] = request.form["description"]
            task["due_date"] = request.form["due_date"]
            tags_input = request.form["tags"]
            task["tags"] = [tag.strip() for tag in tags_input.split(",")] if tags_input else []
            task["priority"] = request.form["priority"]
            if not task["title"]:
                flash("Title is required!", "error")
                return redirect(url_for("edit_task", task_id=task_id))
            if task["due_date"]:
                try:
                    datetime.strptime(task["due_date"], "%Y-%m-%d")
                except ValueError:
                    flash("Invalid date format. Use YYYY-MM-DD.", "error")
                    return redirect(url_for("edit_task", task_id=task_id))
            if task["priority"] not in ["High", "Medium", "Low"]:
                flash("Invalid priority. Choose High, Medium, or Low.", "error")
                return redirect(url_for("edit_task", task_id=task_id))        
            save_tasks(tasks)
            flash("Task updated successfully!", "info")
            return redirect(url_for("index"))
        except Exception as e:
            log_error(f"Error editing task: {e}")
            flash("An error occurred while editing the task.", "error")
            return redirect(url_for("edit_task", task_id=task_id))
    return render_template("edit_task.html", task=task)

@app.route("/complete/<task_id>")
def complete_task(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t["id"]==task_id), None)
    if task:   
        task["completed"] = True
        save_tasks(tasks)
        flash("Task marked as completed!", "success")
    else:
        log_error(f"Task with ID {task_id} not found for completion.")
        flash("Task not found.", "warning")
    return redirect(url_for("index"))

@app.route("/incomplete/<task_id>")
def incomplete_task(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t["id"]==task_id), None)
    if task:
        task["completed"] = False
        save_tasks(tasks)
        flash("Task marked as incompleted!", "info")
    else:
        log_error(f"Task with ID {task_id} not found for incompletion.")
        flash("task not found.", "warning")
    return redirect(url_for("index"))

@app.route("/delete/<task_id>")
def delete_task(task_id):
    tasks = load_tasks()
    original_length = len(tasks)
    tasks = [t for t in tasks if t["id"] != task_id]
    if len(tasks) < original_length:
        save_tasks(tasks)
        flash("Task deleted successfully!", "warning")
    else:
        log_error(f"Task with ID {task_id} not found for deletion.")
        flash("Task not found.", "warning")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)