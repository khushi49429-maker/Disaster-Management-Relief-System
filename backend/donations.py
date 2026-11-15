
from flask import Blueprint, request, jsonify
from database import get_db_connection

donation = Blueprint("donation", __name__)


# CREATE DONATION
@donation.route("/donations", methods=["POST"])
def create_donation():

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "Please provide donation details"
        }), 400

    donor_id = data.get("donor_id")
    emergency_id = data.get("emergency_id")
    donation_type = data.get("donation_type")
    amount = data.get("amount")
    item_name = data.get("item_name")
    quantity = data.get("quantity")

    if not donor_id or not donation_type:
        return jsonify({
            "message": "Donor ID and donation type are required"
        }), 400

    if donation_type not in ["money", "material"]:
        return jsonify({
            "message": "Invalid donation type"
        }), 400

    if donation_type == "money":
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({
                "message": "Enter a valid donation amount"
            }), 400

        item_name = None
        quantity = None

    elif donation_type == "material":
        if not item_name:
            return jsonify({
                "message": "Item name is required for material donation"
            }), 400

        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({
                "message": "Enter a valid item quantity"
            }), 400

        amount = None

    db = get_db_connection()

    if db is None:
        return jsonify({
            "message": "Database connection failed"
        }), 500

    cursor = db.cursor()

    try:
        query = """
        INSERT INTO donations
        (doner_id, emergency_id, donation_type, amount, item_name, quantity)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            donor_id, emergency_id, donation_type,
            amount, item_name, quantity
        )

        cursor.execute(query, values)
        db.commit()

        return jsonify({
            "message": "Donation submitted successfully",
            "donation_id": cursor.lastrowid
        }), 201

    except Exception as error:
        db.rollback()
        return jsonify({
            "message": "Donation submission failed",
            "error": str(error)
        }), 400

    finally:
        cursor.close()
        db.close()


# GET ALL DONATIONS
@donation.route("/donations", methods=["GET"])
def get_donations():

    db = get_db_connection()

    if db is None:
        return jsonify({
            "message": "Database connection failed"
        }), 500

    cursor = db.cursor(dictionary=True)

    try:
        query = """
        SELECT donation_id, doner_id, emergency_id,
               donation_type, amount, item_name,
               quantity, STATUS, created_at
        FROM donations
        ORDER BY created_at DESC
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

# UPDATE DONATION STATUS
@donation.route("/donations/<int:donation_id>", methods=["PUT"])
def update_donation_status(donation_id):

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

        donation_record = cursor.fetchone()

        if donation_record is None:
            return jsonify({"message": "Donation not found"}), 404

        query = """
        UPDATE donations
        SET STATUS = %s
        WHERE donation_id = %s
        """

        cursor.execute(query, (new_status, donation_id))
        db.commit()

        return jsonify({
            "message": "Donation status updated successfully",
            "donation_id": donation_id,
            "status": new_status
        }), 200

    except Exception as error:
        db.rollback()
        return jsonify({
            "message": "Donation status update failed",
            "error": str(error)
        }), 500

    finally:
        cursor.close()
        db.close()