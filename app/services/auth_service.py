from flask import logging
from app.utils.auth_util import hash_password, verify_password, generate_jwt
from app.services.crud_services import get_db_connection

def signup_user(phone, email, password):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Check if email already exists
                cur.execute("SELECT 1 FROM role_users WHERE username = %s", (email,))
                if cur.fetchone():
                    return {"message": "Email already registered", "status": 400}

                # Hash password
                hashed = hash_password(password)

                # Insert user record
                cur.execute(
                    "INSERT INTO role_users (phone, username, password) VALUES (%s, %s, %s)",
                    (phone, email, hashed)
                )
                conn.commit()

        return {"message": "User registered successfully", "status": 201}

    except Exception as e:
        print(e)
        return {"message": "Internal server error", "status": 500}
def login_user(email, password):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Query user details
                cur.execute(
                    "SELECT username, password, role, phone FROM role_users WHERE username = %s",
                    (email,)
                )
                row = cur.fetchone()

        # Check if user exists and password matches
        if not row or not verify_password(password, row[1]):
            return {"message": "Invalid credentials", "status": 401}

        # Generate JWT token
        token = generate_jwt({"user_id": row[0], "email": email})

        return {
            "message": "Login successful",
            "token": token,
            "role": row[2],
            "phone": row[3],
            "status": 200
        }

    except Exception as e:
        logging.error(f"Error in login_user: {str(e)}")
        return {"message": "Internal server error", "status": 500}
