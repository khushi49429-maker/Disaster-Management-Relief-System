
from flask import Blueprint, request, jsonify
from database import get_db_connection

rescue = Blueprint("rescue", __name__)


# ==========================================
# 1. CREATE RESCUE REQUEST
# ==========================================
@rescue.route("/rescue-request", methods=["POST"])
def create_rescue_request():

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "Please provide request details"
        }), 400

    emergency_id = data.get("emergency_id")
    request_by = data.get("requested_by")
    request_details = data.get("request_details")

    if not emergency_id or not request_by:
        return jsonify({
            "message": "Emergency ID and requested_by are required"
        }), 400

    db = get_db_connection()

    if db is None:
        return jsonify({
            "message": "Database connection failed"
        }), 500

    cursor = db.cursor()

    try:
        # Check whether emergency exists
        cursor.execute(
            "SELECT emergency_id, status FROM emergencies WHERE emergency_id = %s",
            (emergency_id,)
        )

        emergency_data = cursor.fetchone()

        if emergency_data is None:
            return jsonify({
                "message": "Emergency not found"
            }), 404

        # Check whether emergency is already resolved
        if emergency_data[1] == "resolved":
            return jsonify({
                "message": "Cannot create rescue request for resolved emergency"
            }), 400

        # Check whether requester exists
        cursor.execute(
            "SELECT user_id FROM users WHERE user_id = %s",
            (request_by,)
        )

        user = cursor.fetchone()

        if user is None:
            return jsonify({
                "message": "Requester not found"
            }), 404

        # Insert rescue request
        query = """
        INSERT INTO rescue_requests
        (emergency_id, requested_by, request_details)
        VALUES (%s, %s, %s)
        """

        cursor.execute(query, (emergency_id, request_by, request_details))
        db.commit()

        return jsonify({
            "message": "Rescue request created successfully",
            "request_id": cursor.lastrowid
        }), 201

    except Exception as error:
        db.rollback()
        return jsonify({
            "message": "Rescue request failed",
            "error": str(error)
        }), 500

    finally:
        cursor.close()
        db.close()


# ==========================================
# 2. GET ALL RESCUE REQUESTS
# ==========================================
@rescue.route("/rescue-request", methods=["GET"])
def get_rescue_requests():

    db = get_db_connection()

    if db is None:
        return jsonify({
            "message": "Database connection failed"
        }), 500

    cursor = db.cursor(dictionary=True)

    try:
        query = """
        SELECT request_id, emergency_id, requested_by,
               assigned_to, request_details, status, created_at
        FROM rescue_requests
        ORDER BY created_at DESC
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


# ==========================================
# 3. UPDATE RESCUE REQUEST STATUS
# ==========================================
@rescue.route("/rescue-request/<int:request_id>", methods=["PUT"])
def update_rescue_request(request_id):

    data = request.get_json()

    if not data or not data.get("status"):
        return jsonify({
            "message": "Please provide a status"
        }), 400

    new_status = data.get("status")

    allowed_statuses = [
        "pending",
        "accepted",
        "in_progress",
        "completed"
    ]

    if new_status not in allowed_statuses:
        return jsonify({
            "message": "Invalid request status"
        }), 400

    db = get_db_connection()

    if db is None:
        return jsonify({
            "message": "Database connection failed"
        }), 500

    cursor = db.cursor()

    try:
        query = """
        UPDATE rescue_requests
        SET status = %s
        WHERE request_id = %s
        """

        cursor.execute(query, (new_status, request_id))

        if cursor.rowcount == 0:
            db.rollback()
            return jsonify({
                "message": "Rescue request not found"
            }), 404

        db.commit()

        return jsonify({
            "message": "Rescue request status updated successfully",
            "request_id": request_id,
            "status": new_status
        }), 200

    except Exception as error:
        db.rollback()
        return jsonify({
            "message": "Status update failed",
            "error": str(error)
        }), 500

    finally:
        cursor.close()
        db.close()


# ==========================================
# 4. ASSIGN VOLUNTEER TO RESCUE REQUEST
# ==========================================
@rescue.route("/rescue-request/<int:request_id>/assign", methods=["PUT"])
def assign_volunteer(request_id):

    data = request.get_json()

    if not data or not data.get("volunteer_id"):
        return jsonify({
            "message": "Volunteer ID is required"
        }), 400

    volunteer_id = data.get("volunteer_id")

    db = get_db_connection()

    if db is None:
        return jsonify({
            "message": "Database connection failed"
        }), 500

    cursor = db.cursor()

    try:
        # Check whether volunteer exists
        cursor.execute(
            """
            SELECT user_id FROM users
            WHERE user_id = %s AND role = 'volunteer'
            """,
            (volunteer_id,)
        )

        volunteer = cursor.fetchone()

        if volunteer is None:
            return jsonify({
                "message": "Volunteer not found"
            }), 404

        # Check whether rescue request exists
        cursor.execute(
            "SELECT status FROM rescue_requests WHERE request_id = %s",
            (request_id,)
        )

        rescue_request = cursor.fetchone()

        if rescue_request is None:
            return jsonify({
                "message": "Rescue request not found"
            }), 404

        # Prevent assignment to completed requests
        if rescue_request[0] == "completed":
            return jsonify({
                "message": "Cannot assign volunteer to completed request"
            }), 400

        # Assign volunteer
        query = """
        UPDATE rescue_requests
        SET assigned_to = %s, status = 'accepted'
        WHERE request_id = %s
        """

        cursor.execute(query, (volunteer_id, request_id))
        db.commit()

        return jsonify({
            "message": "Volunteer assigned successfully",
            "request_id": request_id,
            "volunteer_id": volunteer_id,
            "status": "accepted"
        }), 200

    except Exception as error:
        db.rollback()
        return jsonify({
            "message": "Volunteer assignment failed",
            "error": str(error)
        }), 500

    finally:
        cursor.close()
        db.close()
