from database import get_db_connection

def create_emergency(
    user_id,
    disaster_type,
    location,
    people_affected,
    help_needed,
    description,
    priority
):

    connection = get_db_connection()

    if not connection:
        return False

    cursor = connection.cursor()

    query = """
    INSERT INTO emergency_requests
    (
        user_id,
        disaster_type,
        location,
        people_affected,
        help_needed,
        description,
        priority
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(
        query,
        (
            user_id,
            disaster_type,
            location,
            people_affected,
            help_needed,
            description,
            priority
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    return True


def get_user_emergencies(user_id):

    connection = get_db_connection()

    if not connection:
        return []

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT * FROM emergency_requests
        WHERE user_id=%s
        ORDER BY created_at DESC
        """,
        (user_id,)
    )

    requests = cursor.fetchall()

    cursor.close()
    connection.close()

    return requests