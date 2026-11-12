from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from models.rescue import get_all_emergencies, update_rescue_status
from database import get_db_connection

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin")
def admin_dashboard():

    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("auth.login"))

    connection = get_db_connection()

    if not connection:
        flash("Database connection failed.", "danger")
        return redirect(url_for("index"))

    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM emergency_requests")
    total = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS pending
        FROM emergency_requests
        WHERE status='Pending'
    """)

    pending = cursor.fetchone()["pending"]

    cursor.execute("SELECT COUNT(*) AS users FROM users")

    users = cursor.fetchone()["users"]

    requests = get_all_emergencies()

    cursor.close()
    connection.close()

    return render_template(
        "admin.html",
        total=total,
        pending=pending,
        users=users,
        requests=requests
    )


@admin_bp.route("/update-request/<int:request_id>", methods=["POST"])
def update_request(request_id):

    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))

    status = request.form["status"]

    team = request.form.get("assigned_team", "")

    allowed_status = [
        "Pending",
        "Assigned",
        "In Progress",
        "Resolved"
    ]

    if status not in allowed_status:
        flash("Invalid status.", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    update_rescue_status(request_id, status, team)

    flash("Emergency request updated.", "success")

    return redirect(url_for("admin.admin_dashboard"))