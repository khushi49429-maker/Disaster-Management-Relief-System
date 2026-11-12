from database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

def create_user(name, email, password):

    connection = get_db_connection()

    if not connection:
        return False

    cursor = connection.cursor()

    hashed_password = generate_password_hash(password)

    query = """
    INSERT INTO users
    (name, email, password_hash)
    VALUES (%s, %s, %s)
    """

    try:

        cursor.execute(
            query,
            (name, email, hashed_password)
        )

        connection.commit()

        return True

    except Exception as error:

        print(error)

        return False

    finally:

        cursor.close()
        connection.close()


def login_user(email, password):

    connection = get_db_connection()

    if not connection:
        return None

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM users WHERE email=%s",
        (email,)
    )

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if user and check_password_hash(
        user["password_hash"], password
    ):

        return user

    return None