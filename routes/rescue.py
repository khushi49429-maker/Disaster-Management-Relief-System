from flask import Blueprint, render_template, session, redirect, url_for

from models.rescue import get_all_emergencies

rescue_bp = Blueprint("rescue", __name__)


@rescue_bp.route("/rescue")
def rescue_dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") not in ["admin", "rescue"]:
        return redirect(url_for("dashboard"))

    requests = get_all_emergencies()

    return render_template(
        "rescue.html",
        requests=requests
    )