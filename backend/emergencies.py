from flask import Blueprint, request, jsonify
from database import get_db_connection

emergency = Blueprint("emergency", __name__)

#CREATE EMERGENCY REPORT
@emergency.route("/emergencies", methods=["POST"])
def create_emergency():

    data = request.get_json()

    if not data:
        return jsonify({
            "message":"Please provide emergency details"
        }), 400

    user_id = data.get("user_id")
    title =data.get("title")
    disaster_type = data.get("disaster_type")
    description = data.get("description")
    location = data.get("location")
    severity = data.get("severity", "medium")
    people_affected = data.get("people_affected", 1)

    #valid required fields
    if not all([user_id, title, disaster_type, location]):
        return jsonify({
            "message": "User ID, title, disaster type and location are required"
        }),400

    #valid sverity 
    allowed_severity= ["low", "medium", "high", "critical"]

    if severity not in allowed_severity:
        return jsonify({
            "message": "Invalid sesverity level"
        }),400

    #Validate people affected
    try:
        people_affected = int (people_affected)
        if people_affected<1:
            raise ValueError

    except(ValueError, TypeError):
        return jsonify({
            "message": "People affected must be a positive number"
            }),400

    db= get_db_connection()

    if db is None:
        return jsonify({
            "message": "Database connection failed"
        }), 500

    cursor = db.cursor()

    try:
        query ="""
        INSERT INTO emergencies
        (user_id, title, disaster_type, description,
         location, severity, people_affected)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            user_id,
            title,
            disaster_type,
            description,
            location,
            severity,
            people_affected
        )

        cursor.execute(query, values)
        db.commit()

        return jsonify({
            "message": "Emergency reported successfully",
            "emergency_id": cursor.lastrowid
        }), 201

    except Exception as error:
        db.rollback()

        return jsonify({
            "message": "Emergency report failed",
            "error": str(error)
        }), 400

    finally:
        cursor.close()
        db.close()

#GET ALL EMERGENCY REPORTS
@emergency.route("/emergencies", methods =["GET"])
def get_emergencies():

    db = get_db_connection()

    if db is None:
        return jsonify({
            "message":"Database connection failed"
        }), 500

    cursor = db.cursor (dictionary=True)

    try:
        query="""
        SELECT emergency_id, user_id, title, disaster_type, description, location,severity, people_affected, status, created_at
        FROM emergencies
        ORDER BY created_at DESC
        """
        cursor.execute(query)
        emergencies = cursor.fetchall()

        return jsonify({
            "message": "Emergency reports fetched successfully",
            "total_reports": len(emergencies),
            "emergencies": emergencies
        }),200
    
    except Exception as error:
        return jsonify({
            "message": "Failed to fetch emergency report",
            "error":str(error)
        }), 500

    finally:
        cursor.close()
        db.close()