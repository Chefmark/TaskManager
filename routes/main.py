from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import logging
from models import Task
from extensions import db
from datetime import datetime
import uuid
from utils import log_error, is_valid_date, is_overdue


main_bp = Blueprint('main', __name__)
@main_bp.route("/")
@login_required
def index():
    sort_by = request.args.get("sort", "default")
    filter_tag = request.args.get("tag")
    search_query = request.args.get("search", "").lower()

    tasks = Task.query.filter_by(user_id=current_user.id).all()

    # Apply filters
    if filter_tag:
        tasks = [t for t in tasks if filter_tag in (t.tags or "")]

    if search_query:
        tasks = [
            t for t in tasks
            if search_query in (t.title or "").lower() or search_query in (t.description or "").lower()
        ]

    # Sorting
    if sort_by == "due":
        tasks.sort(key=lambda x: x.due_date or "")
    elif sort_by == "title":
        tasks.sort(key=lambda x: x.title.lower())
    elif sort_by == "status":
        tasks.sort(key=lambda x: x.completed)
    elif sort_by == "priority":
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        tasks.sort(key=lambda x: priority_order.get(x.priority, 1))

    # Overdue flag
    for task in tasks:
        try:
            if task.due_date and not task.completed:
                due = datetime.strptime(task.due_date, "%Y-%m-%d")
                task.is_overdue = datetime.now() > due
            else:
                task.is_overdue = False
        except ValueError:
            task.is_overdue = False

    return render_template("index.html", tasks=tasks, filter_tag=filter_tag, search_query=search_query)

@main_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_task():
    if request.method == "POST":
        try:
            title = request.form["title"].strip()
            description = request.form["description"].strip()
            due_date = request.form["due_date"].strip()
            tags = request.form["tags"].strip()
            priority = request.form["priority"]

            # Input validation
            if not title:
                flash("Title is required!", "error")
                return redirect(url_for("main.add_task"))

            if due_date:
                try:
                    datetime.strptime(due_date, "%Y-%m-%d")
                except ValueError:
                    flash("Invalid date format. Use YYYY-MM-DD.", "error")
                    return redirect(url_for("main.add_task"))

            if priority not in ["High", "Medium", "Low"]:
                flash("Invalid priority. Choose High, Medium, or Low.", "error")
                return redirect(url_for("main.add_task"))

            # Create and save task to database
            new_task = Task(
                id=str(uuid.uuid4()),
                title=title,
                description=description,
                due_date=due_date,
                completed=False,
                tags=tags,
                priority=priority,
                user_id=current_user.id
            )
            db.session.add(new_task)
            db.session.commit()

            flash("Task added successfully!", "success")
            return redirect(url_for("main.index"))

        except Exception as e:
            log_error(f"Error adding task: {e}")
            flash("An error occurred while adding the task.", "error")
            return redirect(url_for("main.add_task"))

    return render_template("add_task.html")

@main_bp.route("/edit/<task_id>", methods =["GET", "POST"])
@login_required
def edit_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()

    if not task:
        flash("Task not found or unauthorized access.", "warning")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        try:
            title = request.form["title"].strip()
            description = request.form["description"].strip()
            due_date = request.form["due_date"].strip()
            tags_input = request.form["tags"].strip()
            priority = request.form["priority"]

            # Validation
            if not title:
                flash("Title is required!", "error")
                return redirect(url_for("main.edit_task", task_id=task_id))

            if due_date:
                try:
                    datetime.strptime(due_date, "%Y-%m-%d")
                except ValueError:
                    flash("Invalid date format. Use YYYY-MM-DD.", "error")
                    return redirect(url_for("main.edit_task", task_id=task_id))

            if priority not in ["High", "Medium", "Low"]:
                flash("Invalid priority.", "error")
                return redirect(url_for("main.edit_task", task_id=task_id))

            # Update task
            task.title = title
            task.description = description
            task.due_date = due_date
            task.tags = tags_input
            task.priority = priority

            db.session.commit()
            flash("Task updated successfully!", "info")
            return redirect(url_for("main.index"))

        except Exception as e:
            log_error(f"Error editing task {task_id}: {e}")
            flash("An error occurred while updating the task.", "error")
            return redirect(url_for("main.edit_task", task_id=task_id))

    return render_template("edit_task.html", task=task)

@main_bp.route("/complete/<task_id>")
@login_required
def complete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if task:
        task.completed = True
        db.session.commit()
        flash("Task marked as completed!", "success")
    else:
        flash("Task not found or unauthorized access.", "warning")
    return redirect(url_for("main.index"))

@main_bp.route("/incomplete/<task_id>")
@login_required
def incomplete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if task:
        task.completed = False
        db.session.commit()
        flash("Task marked as incompleted!", "info")
    else:
        flash("Task not found or unauthorized access.", "warning")
    return redirect(url_for("main.index"))

@main_bp.route("/delete/<task_id>")
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if task:
        db.session.delete(task)
        db.session.commit()
        flash("Task deleted successfully!", "warning")
    else:
        flash("Task not found or unauthorized access.", "warning")
    return redirect(url_for("main.index"))

@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")