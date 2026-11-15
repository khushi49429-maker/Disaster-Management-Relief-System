from flask import Blueprint, request, jsonify
from database import get_db_connection

rescue =Blueprint("rescue", __name__)

#CREATE RESCUE REQUEST
@rescue.route("/rescue-request", methods=["POST"])
def create_recue_request():

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "Please provide request details"
        }),400

    emergency_id= data.get("emergency_id")
    request_by = data.get("requested_by")
    request_details= data.get("request_details")

    if not emergency_id or not request_by:
        return jsonify({
            "message": "Emergency ID and requested_by are required"
        }), 400

    db = get_db_connection()

    if db is None:
        return jsonify({
            "message" : "Database connection failed"
        }),500

    cursor = db.cursor()

    try:
        query= """
        INSERT INTO rescue_requests
        (emergency_id,requested_by, request_details)
        VALUES (%s, %s, %s)
        """
        values = (emergency_id, request_by, request_details)

        cursor.execute(query,values)
        db.commit()

        return jsonify({
            "message" : "Rescue request created successfully",
            "requested_id" : cursor.lastrowid
        }),201

    except Exception as error:
        db.rollback()
        return jsonify({
            "message":"Rescue request failed",
            "error" : str(error)
        }),400

    finally:
        cursor.close()
        db.close()


# GET ALL RESCUE REQUESTS
@rescue.route("/rescue-request", methods=["GET"])
def get_rescue_requests():

    db = get_db_connection()

    if db is None:
        return jsonify({"message": "Database connection failed"}), 500

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

{
  "message": "Rescue requests fetched successfully",
  "rescue_requests": [
    {
      "assigned_to": None,
      "created_at": "Fri, 13 Nov 2026 18:29:31 GMT",
      "emergency_id": 1,
      "request_details": "I need food, drinking water and medical assistance.",
      "request_id": 1,
      "requested_by": 1,
      "status": "pending"
    }
  ],
  "total_requests": 1
}

# UPDATE RESCUE REQUEST STATUS
@rescue.route("/rescue-request/<int:request_id>", methods=["PUT"])
def update_rescue_request(request_id):
    data = request.get_json()

    if not data or not data.get("status"):
        return jsonify({"message": "Please provide a status"}), 400

    new_status = data.get("status")
    allowed_statuses = ["pending", "accepted", "in_progress", "completed"]

    if new_status not in allowed_statuses:
        return jsonify({"message": "Invalid request status"}), 400

    db = get_db_connection()
    if db is None:
        return jsonify({"message": "Database connection failed"}), 500

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
            return jsonify({"message": "Rescue request not found"}), 404

        db.commit()
        return jsonify({
            "message": "Rescue request status updated successfully",
            "request_id": request_id,
            "status": new_status
        }), 200

    except Exception as error:
        db.rollback()
        return jsonify({"message": "Status update failed", "error": str(error)}), 500

    finally:
        cursor.close()
        db.close()

 # ASSIGN VOLUNTEER TO RESCUE REQUEST
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
        # Check whether volunteer exists and has volunteer role
        query = """
        SELECT user_id
        FROM users
        WHERE user_id = %s AND role = 'volunteer'
        """
        cursor.execute(query, (volunteer_id,))
        volunteer = cursor.fetchone()

        if volunteer is None:
            return jsonify({
                "message": "Volunteer not found"
            }), 404

 # Check whether rescue request exists
        query = """
        SELECT request_id
        FROM rescue_requests
        WHERE request_id = %s
        """
        cursor.execute(query, (request_id,))
        rescue_request = cursor.fetchone()

        if rescue_request is None:
            return jsonify({
                "message": "Rescue request not found"
            }), 404

        # Assign volunteer and update status
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