from flask import Flask, render_template,session,redirect,url_for
from backend.auth import auth
from backend.emergencies import emergency
from backend.rescue import rescue
from backend.donations import donation
from backend.admin import admin

app = Flask(__name__)
app.secret_key = "your_secure_secret_key"

# Register backend APIs
app.register_blueprint(auth)
app.register_blueprint(emergency)
app.register_blueprint(rescue)
app.register_blueprint(donation)
app.register_blueprint(admin)


# FRONTEND PAGE ROUTES

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/register")
def register_page():
    return render_template("register.html")


@app.route("/user-dashboard")
def user_dashboard():
    return render_template("user_dashboard.html")


@app.route("/emergency")
def emergency_page():
    return render_template("emergency_page.html")


@app.route("/alerts")
def alerts_page():
    return render_template("alerts_page.html")


@app.route("/rescue-dashboard")
def rescue_dashboard():
    return render_template("rescue_dashboard.html")


@app.route("/admin-dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/donate")
def donate_page():
    return render_template("donate.html")

if __name__ == "__main__":
    app.run(debug=True)
