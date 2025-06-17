from app.utils.auth_util import hash_password, verify_password, generate_jwt
from app.services.crud_services import get_db_connection

def signup_user(phone,email, password):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM role_users WHERE username = %s", (email,))
    if cur.fetchone():
        cur.close()
        conn.close()
        return {"message": "Email already registered", "status": 400}
    print(111)
    hashed = hash_password(password)
    cur.execute("INSERT INTO role_users (phone,username, password) VALUES (%s,%s, %s)", (phone,email, hashed))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "User registered successfully", "status": 201}

def login_user(email, password):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT username, password,role FROM role_users WHERE username = %s", (email,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row or not verify_password(password, row[1]):
        return {"message": "Invalid credentials", "status": 401}

    token = generate_jwt({"user_id": row[0], "email": email})
    return {"message": "Login successful", "token": token,"role":row[2] ,"status": 200}
