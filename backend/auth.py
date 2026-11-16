
from flask import Blueprint, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection

auth = Blueprint("auth", __name__)


# ==========================================
# 1. USER REGISTRATION
# ==========================================
@auth.route("/register", methods=["POST"])
def register():

    data = request.get_json(silent=True) or request.form

    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    gender = data.get("gender")
    password = data.get("password")
    confirm_password = data.get("confirm_password")

    # Validate required fields
    if not all([name, email, password, confirm_password]):
        return jsonify({
            "message": "Please fill all required fields"
        }), 400

    # Check password confirmation
    if password != confirm_password:
        return jsonify({
            "message": "Passwords do not match"
        }), 400

    # Validate gender
    allowed_genders = [
        "male",
        "female",
        "other",
        "prefer_not_to_say"
    ]

    if gender and gender not in allowed_genders:
        return jsonify({
            "message": "Invalid gender selection"
        }), 400

    # Hash password
    hashed_password = generate_password_hash(password)

    db = get_db_connection()

    if db is None:
        return jsonify({
            "message": "Database connection failed"
        }), 500

    cursor = db.cursor()

    try:
        query = """
        INSERT INTO users (name, email, phone, gender, password)
        VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            name,
            email,
            phone,
            gender or "prefer_not_to_say",
            hashed_password
        )

        cursor.execute(query, values)
        db.commit()

        if request.is_json:
            return jsonify({
                "message": "Registration successful"
            }), 201

        return redirect(url_for("login_page"))

    except Exception as error:
        db.rollback()

        return jsonify({
            "message": "Registration failed",
            "error": str(error)
        }), 400

    finally:
        cursor.close()
        db.close()


# ==========================================
# 2. USER LOGIN
# ==========================================
@auth.route("/login", methods=["POST"])
def login():

    data = request.get_json(silent=True) or request.form

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "message": "Email and password are required"
        }), 400

    db = get_db_connection()

    if db is None:
        return jsonify({
            "message": "Database connection failed"
        }), 500

    cursor = db.cursor()

    try:
        query = """
        SELECT user_id, name, email, phone, gender, password, role
        FROM users
        WHERE email = %s
        """

        cursor.execute(query, (email,))
        user = cursor.fetchone()

        # Check user exists
        if user is None:
            return jsonify({
                "message": "Invalid email or password"
            }), 401

        # Verify password
        stored_password = user[5]

        if not check_password_hash(stored_password, password):
            return jsonify({
                "message": "Invalid email or password"
            }), 401

        # Create session
        session.clear()
        session["user_id"] = user[0]
        session["role"] = user[6]

        # JSON login response
        if request.is_json:
            return jsonify({
                "message": "Login successful",
                "user": {
                    "user_id": user[0],
                    "name": user[1],
                    "email": user[2],
                    "phone": user[3],
                    "gender": user[4],
                    "role": user[6]
                }
            }), 200

        # Role-based redirection
        if user[6] == "admin":
            return redirect(url_for("admin_dashboard"))

        elif user[6] == "volunteer":
            return redirect(url_for("rescue_dashboard"))

        else:
            return redirect(url_for("user_dashboard"))

    except Exception as error:
        return jsonify({
            "message": "Login failed",
            "error": str(error)
        }), 500

    finally:
        cursor.close()
        db.close()
