from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from models.user import create_user, login_user

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "danger")
            return redirect(url_for("auth.register"))

        result = create_user(name, email, password)

        if result:

            flash("Registration successful!", "success")

            return redirect(url_for("auth.login"))

        flash("Registration failed. Email may already exist.", "danger")

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = login_user(email, password)

        if user:

            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]

            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


@auth.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully.", "success")

    return redirect(url_for("index"))