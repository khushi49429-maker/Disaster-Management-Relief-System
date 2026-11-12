from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from models.donation import create_donation

donation_bp = Blueprint("donation", __name__)


@donation_bp.route("/donation", methods=["GET", "POST"])
def donate():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        result = create_donation(

            session["user_id"],

            request.form["donation_type"],

            request.form["quantity"],

            request.form.get("contact", "")

        )

        if result:

            flash("Thank you for your donation!", "success")

            return redirect(url_for("dashboard"))

        flash("Donation submission failed.", "danger")

    return render_template("donation.html")