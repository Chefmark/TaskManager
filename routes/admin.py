from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import User
from extensions import db
from utils import log_error, is_valid_date, is_overdue

admin_bp = Blueprint('admin', __name__)

@admin_bp.route("/admin")
@login_required
def admin_dashboard():
    if not current_user.is_admin_user():
        flash("Access denied: Admins only.", "danger")
        return redirect(url_for("main.index"))
    return render_template("admin.html")

@admin_bp.route("/admin/users")
@login_required
def user_management():
    if not current_user.is_admin_user():
        flash("Access denied: Admins only.", "danger")
        return redirect(url_for("main.index"))

    users = User.query.all()
    return render_template("user_management.html", users=users)

@admin_bp.route("/admin/delete_user/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    if not current_user.is_admin_user():
        flash("Access denied.", "danger")
        return redirect(url_for("main.index"))

    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "warning")
        return redirect(url_for("admin.user_management"))

    if request.form.get("confirm") == "delete":
        db.session.delete(user)
        db.session.commit()
        flash(f"User '{user.username}' deleted.", "success")
    else:
        flash("Deletion cancelled or not confirmed.", "info")

    return redirect(url_for("admin.user_management"))

@admin_bp.route("/admin/create_user", methods=["GET", "POST"])
@login_required
def create_user():
    if not current_user.is_admin_user():
        flash("Access denied: Admins only.", "danger")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        is_admin = request.form.get("is_admin") == "on"

        if not username or not password:
            flash("Username and password are required.", "warning")
            return redirect(url_for("admin.create_user"))

        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "warning")
            return redirect(url_for("admin.create_user"))

        new_user = User(username=username, is_admin=is_admin)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash(f"User {username} created successfully.", "success")
        return redirect(url_for("admin.admin_dashboard"))

    return render_template("create_user.html")

@admin_bp.route("/admin/edit_user/<int:user_id>", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    if not current_user.is_admin_user():
        flash("Access denied.", "danger")
        return redirect(url_for("main.index"))

    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "warning")
        return redirect(url_for("admin.user_management"))

    if request.method == "POST":
        username = request.form["username"].strip()
        is_admin = request.form.get("is_admin") == "on"

        if not username:
            flash("Username is required.", "warning")
            return redirect(url_for("admin.edit_user", user_id=user_id))

        user.username = username
        user.is_admin = is_admin
        db.session.commit()
        flash("User updated successfully.", "success")
        return redirect(url_for("admin.user_management"))

    return render_template("edit_user.html", user=user)
