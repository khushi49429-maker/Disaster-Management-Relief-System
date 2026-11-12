from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from models.emergency import (
    create_emergency,
    get_user_emergencies
)

emergency_bp = Blueprint("emergency", __name__)


@emergency_bp.route("/emergency", methods=["GET", "POST"])
def emergency():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        result = create_emergency(

            session["user_id"],

            request.form["disaster_type"],

            request.form["location"],

            request.form["people_affected"],

            request.form["help_needed"],

            request.form["description"],

            request.form["priority"]

        )

        if result:

            flash("Emergency request submitted!", "success")

            return redirect(url_for("dashboard"))

        flash("Unable to submit request.", "danger")

    return render_template("emergency.html")