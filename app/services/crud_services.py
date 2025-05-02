import psycopg2


DB_CONFIG = {
    "user": "postgres.dmepnqgumjlvwaqnaybp",
    "password": "Kamsaf@786",
    "host": "aws-0-ap-south-1.pooler.supabase.com",
    "port": "6543",
    "dbname": "postgres"
}
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


def user_exists(user_id=None, phone=None):

    if not user_id and not phone:
        return {"status": "error", "message": "Provide either 'id' or 'phone' to check."}, 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                if user_id:
                    cur.execute("SELECT id, phone, name, lastlogin, language FROM users WHERE id = %s;", (user_id,))
                else:
                    cur.execute("SELECT id, phone, name, lastlogin, language FROM users WHERE phone = %s;", (phone,))

                user = cur.fetchone()

                if user:
                    return {
                        "exists": True,
                        "message": "User exists.",
                        "user": {
                            "id": user[0],
                            "phone": user[1],
                            "name": user[2],
                            "lastlogin": user[3],
                            "language": user[4]
                        }
                    }, 200
                else:
                    return {"exists": False, "message": "User does not exist."}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 400

def insert_user(user_data):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO users (id, phone, name, lastlogin, language)
                    VALUES (%s, %s, %s, %s, %s);
                """, (
                    user_data['id'],
                    user_data['phone'],
                    user_data['name'],
                    user_data['lastlogin'],
                    user_data['language']
                ))
        return {"status": "success", "message": "User added."}, 201
    except Exception as e:
        return {"status": "error", "message": str(e)}, 400

def insert_order(data):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Generate order ID: YYYYMMDD### using PostgreSQL syntax
                cur.execute("""
                    SELECT TO_CHAR(NOW(), 'YYYYMMDD') || 
                           LPAD((COUNT(*) + 1)::TEXT, 3, '0') AS order_id
                    FROM orders
                    WHERE created_at::date = CURRENT_DATE;
                """)
                order_id = cur.fetchone()[0]

                # Insert order without feedback
                cur.execute("""
                    INSERT INTO orders (id, receipt, bill_amount, userid, created_at)
                    VALUES (%s, %s, %s, %s, NOW());
                """, (order_id, data['receipt'], data['bill_amount'], data['userid']))

        return {"status": "success", "message": "Order added.", "order_id": order_id}, 201
    except Exception as e:
        return {"status": "error", "message": str(e)}, 400
