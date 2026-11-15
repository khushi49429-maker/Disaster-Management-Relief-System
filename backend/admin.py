from flask import Blueprint, jsonify, session
admin = Blueprint("admin",__name__)
from database import get_db_connection

admin = Blueprint("admin", __name__)


#1. ADMIN DASHBOARD SUMMARY
@admin.route("/admin/dashboard", methods=["GET"])
def admin_dashboard():

    db = get_db_connection()

    if db is None:
        return jsonify({
            "message": "Database connection failed"
        }), 500

    cursor = db.cursor(dictionary=True)

    try:
        query = """
        SELECT
            (SELECT COUNT(*) FROM users) AS total_users,

            (SELECT COUNT(*) FROM users
             WHERE role = 'volunteer') AS total_volunteers,

            (SELECT COUNT(*) FROM emergencies) AS total_emergencies,

            (SELECT COUNT(*) FROM rescue_requests
             WHERE status = 'pending') AS pending_rescue_requests,

            (SELECT COUNT(*) FROM donations) AS total_donations,

            (SELECT COUNT(*) FROM donations
             WHERE STATUS = 'pending') AS pending_donations
        """

        cursor.execute(query)
        dashboard_data = cursor.fetchone()

        return jsonify({
            "message": "Admin dashboard data fetched successfully",
            "dashboard": dashboard_data
        }), 200

    except Exception as error:
        return jsonify({
            "message": "Failed to fetch dashboard data",
            "error": str(error)
        }), 500

    finally:
        cursor.close()
        db.close()

#2. VIEW ALL USERS
@admin.route("/admin/users", methods=["GET"])
def get_all_users():

    db = get_db_connection()

    if db is None:
        return jsonify({"message": "Database connection failed"}), 500

    cursor = db.cursor(dictionary=True)

    try:
        query = """
        SELECT user_id, name, email, phone, gender, role, created_at
        FROM users
        ORDER BY created_at DESC
        """

        cursor.execute(query)
        users = cursor.fetchall()

        return jsonify({
            "message": "Users fetched successfully",
            "total_users": len(users),
            "users": users
        }), 200

    except Exception as error:
        return jsonify({
            "message": "Failed to fetch users",
            "error": str(error)
        }), 500

    finally:
        cursor.close()
        db.close()

#3. VIEW ALL VOLUNTEERS
@admin.route("/admin/volunteers", methods=["GET"])
def get_all_volunteers():

    db = get_db_connection()

    if db is None:
        return jsonify({"message": "Database connection failed"}), 500

    cursor = db.cursor(dictionary=True)

    try:
        query = """
        SELECT user_id, name, email, phone, gender, created_at
        FROM users
        WHERE role = 'volunteer'
        ORDER BY created_at DESC
        """

        cursor.execute(query)
        volunteers = cursor.fetchall()

        return jsonify({
            "message": "Volunteers fetched successfully",
            "total_volunteers": len(volunteers),
            "volunteers": volunteers
        }), 200

    except Exception as error:
        return jsonify({
            "message": "Failed to fetch volunteers",
            "error": str(error)
        }), 500

    finally:
        cursor.close()
        db.close()

#4. UPDATE USER ROLE
@admin.route("/admin/users/<int:user_id>/role", methods=["PUT"])
def update_user_role(user_id):

    from flask import request

    data = request.get_json()

    if not data or not data.get("role"):
        return jsonify({"message": "Please provide a role"}), 400

    new_role = data.get("role")

    allowed_roles = ["user", "volunteer"]

    if new_role not in allowed_roles:
        return jsonify({"message": "Invalid role"}), 400

    db = get_db_connection()

    if db is None:
        return jsonify({"message": "Database connection failed"}), 500

    cursor = db.cursor()

    try:
        # Check whether user exists
        cursor.execute(
            "SELECT user_id FROM users WHERE user_id = %s",
            (user_id,)
        )

        user = cursor.fetchone()

        if user is None:
            return jsonify({"message": "User not found"}), 404

        # Update user role
        cursor.execute(
            "UPDATE users SET role = %s WHERE user_id = %s",
            (new_role, user_id)
        )

        db.commit()

        return jsonify({
            "message": "User role updated successfully",
            "user_id": user_id,
            "new_role": new_role
        }), 200

    except Exception as error:
        db.rollback()

        return jsonify({
            "message": "Failed to update user role",
            "error": str(error)
        }), 500

    finally:
        cursor.close()
        db.close()

#5. VIEW ALL EMERGENCIES
@admin.route("/admin/emergencies", methods=["GET"])
def get_all_emergencies():

    db = get_db_connection()

    if db is None:
        return jsonify({"message": "Database connection failed"}), 500

    cursor = db.cursor(dictionary=True)

    try:
        query = """
        SELECT
            emergency_id,
            user_id,
            title,
            disaster_type,
            description,
            location,
            severity,
            people_affected,
            status,
            created_at
        FROM emergencies
        ORDER BY created_at DESC
        """

        cursor.execute(query)
        emergencies = cursor.fetchall()

        return jsonify({
            "message": "Emergencies fetched successfully",
            "total_emergencies": len(emergencies),
            "emergencies": emergencies
        }), 200

    except Exception as error:
        return jsonify({
            "message": "Failed to fetch emergencies",
            "error": str(error)
        }), 500

    finally:
        cursor.close()
        db.close()

#6. VIEW ALL RESCUE REQUESTS
@admin.route("/admin/rescue-requests", methods=["GET"])
def get_all_rescue_requests():

    db = get_db_connection()

    if db is None:
        return jsonify({"message": "Database connection failed"}), 500

    cursor = db.cursor(dictionary=True)

    try:
        query = """
        SELECT
            r.request_id,
            r.emergency_id,
            e.title AS emergency_title,
            e.location AS emergency_location,
            r.requested_by,
            u.name AS requester_name,
            r.assigned_to,
            v.name AS volunteer_name,
            r.request_details,
            r.status,
            r.created_at
        FROM rescue_requests r
        JOIN emergencies e
            ON r.emergency_id = e.emergency_id
        JOIN users u
            ON r.requested_by = u.user_id
        LEFT JOIN users v
            ON r.assigned_to = v.user_id
        ORDER BY r.created_at DESC
        """

        cursor.execute(query)
        requests_list = cursor.fetchall()

        return jsonify({
            "message": "Rescue requests fetched successfully",
            "total_requests": len(requests_list),
            "rescue_requests": requests_list
        }), 200

    except Exception as error:
        return jsonify({
            "message": "Failed to fetch rescue requests",
            "error": str(error)
        }), 500

    finally:
        cursor.close()
        db.close()

#7. VIEW ALL DONATIONS
@admin.route("/admin/donations", methods=["GET"])
def get_all_donations():

    db = get_db_connection()

    if db is None:
        return jsonify({"message": "Database connection failed"}), 500

    cursor = db.cursor(dictionary=True)

    try:
        query = """
        SELECT
            d.donation_id,
            d.doner_id AS donor_id,
            u.name AS donor_name,
            d.emergency_id,
            e.title AS emergency_title,
            d.donation_type,
            d.amount,
            d.item_name,
            d.quantity,
            d.STATUS AS status,
            d.created_at
        FROM donations d
        JOIN users u
            ON d.doner_id = u.user_id
        LEFT JOIN emergencies e
            ON d.emergency_id = e.emergency_id
        ORDER BY d.created_at DESC
        """

        cursor.execute(query)
        donations = cursor.fetchall()

        return jsonify({
            "message": "Donations fetched successfully",
            "total_donations": len(donations),
            "donations": donations
        }), 200

    except Exception as error:
        return jsonify({
            "message": "Failed to fetch donations",
            "error": str(error)
        }), 500

    finally:
        cursor.close()
        db.close()


#8. UPDATE DONATION STATUS

@admin.route("/admin/donations/<int:donation_id>/status", methods=["PUT"])
def update_donation_status(donation_id):
    from flask import request

    data = request.get_json()

    if not data or not data.get("status"):
        return jsonify({"message": "Please provide donation status"}), 400

    new_status = data.get("status")
    allowed_statuses = ["pending", "received", "distributed"]

    if new_status not in allowed_statuses:
        return jsonify({"message": "Invalid donation status"}), 400

    db = get_db_connection()

    if db is None:
        return jsonify({"message": "Database connection failed"}), 500

    cursor = db.cursor()

    try:
        cursor.execute(
            "SELECT donation_id FROM donations WHERE donation_id = %s",
            (donation_id,)
        )

        donation = cursor.fetchone()

        if donation is None:
            return jsonify({"message": "Donation not found"}), 404

        cursor.execute(
            "UPDATE donations SET STATUS = %s WHERE donation_id = %s",
            (new_status, donation_id)
        )

        db.commit()

        return jsonify({
            "message": "Donation status updated successfully",
            "donation_id": donation_id,
            "new_status": new_status
        }), 200

    except Exception as error:
        db.rollback()
        return jsonify({
            "message": "Failed to update donation status",
            "error": str(error)
        }), 500

    finally:
        cursor.close()
        db.close()


#9. VIEW EMERGENCY DETAILS BY ID

@admin.route("/admin/emergencies/<int:emergency_id>", methods=["GET"])
def get_emergency_details(emergency_id):

    db = get_db_connection()

    if db is None:
        return jsonify({"message": "Database connection failed"}), 500

    cursor = db.cursor(dictionary=True)

    try:
        query = """
        SELECT
            e.emergency_id,
            e.user_id,
            u.name AS reporter_name,
            u.email AS reporter_email,
            u.phone AS reporter_phone,
            e.title,
            e.disaster_type,
            e.description,
            e.location,
            e.severity,
            e.people_affected,
            e.status,
            e.created_at
        FROM emergencies e
        JOIN users u ON e.user_id = u.user_id
        WHERE e.emergency_id = %s
        """

        cursor.execute(query, (emergency_id,))
        emergency_data = cursor.fetchone()

        if emergency_data is None:
            return jsonify({"message": "Emergency not found"}), 404

        return jsonify({
            "message": "Emergency details fetched successfully",
            "emergency": emergency_data
        }), 200

    except Exception as error:
        return jsonify({
            "message": "Failed to fetch emergency details",
            "error": str(error)
        }), 500

    finally:
        cursor.close()
        db.close()


# UPDATE EMERGENCY STATUS

@admin.route("/admin/emergencies/<int:emergency_id>/status", methods=["PUT"])
def update_emergency_status(emergency_id):
    from flask import request

    data = request.get_json()

    if not data or not data.get("status"):
        return jsonify({"message": "Please provide emergency status"}), 400

    new_status = data.get("status")
    allowed_statuses = ["reported", "verified", "in_progress", "resolved"]

    if new_status not in allowed_statuses:
        return jsonify({"message": "Invalid emergency status"}), 400

    db = get_db_connection()

    if db is None:
        return jsonify({"message": "Database connection failed"}), 500

    cursor = db.cursor()

    try:
        cursor.execute(
            "SELECT emergency_id FROM emergencies WHERE emergency_id = %s",
            (emergency_id,)
        )

        emergency = cursor.fetchone()

        if emergency is None:
            return jsonify({"message": "Emergency not found"}), 404

        cursor.execute(
            "UPDATE emergencies SET status = %s WHERE emergency_id = %s",
            (new_status, emergency_id)
        )

        db.commit()

        return jsonify({
            "message": "Emergency status updated successfully",
            "emergency_id": emergency_id,
            "new_status": new_status
        }), 200

    except Exception as error:
        db.rollback()
        return jsonify({
            "message": "Failed to update emergency status",
            "error": str(error)
        }), 500

    finally:
        cursor.close()
        db.close()


# ADMIN UPDATE RESCUE REQUEST STATUS

@admin.route("/admin/rescue-requests/<int:request_id>/status", methods=["PUT"])
def admin_update_rescue_status(request_id):
    from flask import request

    data = request.get_json()
    new_status = data.get("status") if data else None

    allowed_statuses = ["pending", "accepted", "in_progress", "completed"]

    if new_status not in allowed_statuses:
        return jsonify({"message": "Invalid or missing rescue request status"}), 400

    db = get_db_connection()
    if db is None:
        return jsonify({"message": "Database connection failed"}), 500

    cursor = db.cursor()

    try:
        cursor.execute(
            "SELECT request_id FROM rescue_requests WHERE request_id = %s",
            (request_id,)
        )

        if cursor.fetchone() is None:
            return jsonify({"message": "Rescue request not found"}), 404

        cursor.execute(
            "UPDATE rescue_requests SET status = %s WHERE request_id = %s",
            (new_status, request_id)
        )
        db.commit()

        return jsonify({
            "message": "Rescue request status updated successfully",
            "request_id": request_id,
            "new_status": new_status
        }), 200

    except Exception as error:
        db.rollback()
        return jsonify({"message": "Update failed", "error": str(error)}), 500

    finally:
        cursor.close()
        db.close()



# ADMIN VIEW RESCUE REQUEST DETAILS

@admin.route("/admin/rescue-requests/<int:request_id>", methods=["GET"])
def get_rescue_request_details(request_id):

    db = get_db_connection()
    if db is None:
        return jsonify({"message": "Database connection failed"}), 500

    cursor = db.cursor(dictionary=True)

    try:
        query = """
        SELECT
            r.request_id,
            r.emergency_id,
            e.title AS emergency_title,
            e.location AS emergency_location,
            r.requested_by,
            u.name AS requester_name,
            r.assigned_to,
            v.name AS volunteer_name,
            r.request_details,
            r.status,
            r.created_at
        FROM rescue_requests r
        JOIN emergencies e ON r.emergency_id = e.emergency_id
        JOIN users u ON r.requested_by = u.user_id
        LEFT JOIN users v ON r.assigned_to = v.user_id
        WHERE r.request_id = %s
        """

        cursor.execute(query, (request_id,))
        rescue_data = cursor.fetchone()

        if rescue_data is None:
            return jsonify({"message": "Rescue request not found"}), 404

        return jsonify({
            "message": "Rescue request details fetched successfully",
            "rescue_request": rescue_data
        }), 200

    except Exception as error:
        return jsonify({
            "message": "Failed to fetch rescue request details",
            "error": str(error)
        }), 500

    finally:
        cursor.close()
        db.close()

# ADMIN AUTHORIZATION
@admin.before_request
def check_admin_access():

    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    if session.get("role") != "admin":
        return jsonify({"message": "Admin access only"}), 403