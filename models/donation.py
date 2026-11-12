from database import get_db_connection

def create_donation(user_id, donation_type, quantity, contact):

    connection = get_db_connection()

    if not connection:
        return False

    cursor = connection.cursor()

    query = """
    INSERT INTO donations
    (user_id, donation_type, quantity, contact)
    VALUES (%s,%s,%s,%s)
    """

    cursor.execute(
        query,
        (user_id, donation_type, quantity, contact)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return True


def get_all_donations():

    connection = get_db_connection()

    if not connection:
        return []

    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM donations ORDER BY created_at DESC")

    donations = cursor.fetchall()

    cursor.close()
    connection.close()

    return donations