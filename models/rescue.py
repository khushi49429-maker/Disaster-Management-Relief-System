from database import get_db_connection

def get_all_emergencies():

    connection = get_db_connection()

    if not connection:
        return []

    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM emergency_requests
        ORDER BY FIELD(priority,
        'Critical','High','Medium','Low'),
        created_at DESC
    """)

    requests = cursor.fetchall()

    cursor.close()
    connection.close()

    return requests


def update_rescue_status(request_id, status, team_name):

    connection = get_db_connection()

    if not connection:
        return False

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE emergency_requests
        SET status=%s, assigned_team=%s
        WHERE id=%s
    """, (status, team_name, request_id))

    connection.commit()

    cursor.close()
    connection.close()

    return True