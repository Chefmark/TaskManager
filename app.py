from flask import Flask,flash, render_template, request, redirect, url_for
import json
import os
from datetime import datetime
from key import flashkey as fkey
import uuid


app = Flask(__name__)
app.secret_key = fkey

# Load and save tasks from JSON
def load_tasks(): 
    if os.path.exists("tasks.json"):
        try:
            with open("tasks.json", "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
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
        title = request.form["title"]
        description = request.form["description"]
        due_date = request.form["due_date"]
        tags = request.form["tags"].split(",") if request.form["tags"] else []
        priority = request.form["priority"]
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
    return render_template("add_task.html")

@app.route("/edit/<task_id>", methods =["GET", "POST"])
def edit_task(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t["id"]==task_id), None)
    if not task:
        return "Task not found", 404

    if request.method == "POST":
        task["title"] = request.form["title"]
        task["description"] = request.form["description"]
        task["due_date"] = request.form["due_date"]
        tags_input = request.form["tags"]
        task["tags"] = [tag.strip() for tag in tags_input.split(",")] if tags_input else []
        task["priority"] = request.form["priority"]
        save_tasks(tasks)
        flash("Task updated successfully!", "info")
        return redirect(url_for("index"))
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
        flash("task not found.", "warning")
    return redirect(url_for("index"))

@app.route("/delete/<task_id>")
def delete_task(task_id):
    tasks = load_tasks()
    original_length = len(tasks)
    tasks = [t for t in tasks if t["id]"] != task_id]
    if len(tasks) < original_length:
        save_tasks(tasks)
        flash("Task deleted successfully!", "warning")
    else:
        flash("Task not found.", "warning")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)