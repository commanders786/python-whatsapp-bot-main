from flask import Blueprint, request, jsonify
import psycopg2

from app.services.crud_services import insert_order, insert_user, user_exists
from app.services.product_service import fetch_and_categorize_products, send_whatsapp_product_list

crud_blueprint = Blueprint("crud", __name__)

# Connection config - You can later refactor this into a separate config file
DB_CONFIG = {
    "user": "postgres.dmepnqgumjlvwaqnaybp",
    "password": "Kamsaf@786",
    "host": "aws-0-ap-south-1.pooler.supabase.com",
    "port": "6543",
    "dbname": "postgres"
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# ------------------ USERS ------------------

@crud_blueprint.route("/users", methods=["POST"])
def add_user():
    data = request.get_json()
    response, status = insert_user(data)
    return jsonify(response), status


@crud_blueprint.route("/users", methods=["GET"])
def get_users():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, phone, name, lastlogin, language,created_at FROM users;")
                users = cur.fetchall()
                result = [
                    {"id": u[0], "phone": u[1], "name": u[2], "lastlogin": u[3], "language": u[4],"created_at":u[5]}
                    for u in users
                ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# ------------------ ORDERS ------------------

@crud_blueprint.route("/orders", methods=["POST"])
def add_order():
    data = request.get_json()
    response, status_code = insert_order(data)
    return jsonify(response), status_code


@crud_blueprint.route("/orders", methods=["GET"])
def get_orders():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, created_at, feedback, receipt, bill_amount, userid FROM orders;")
                orders = cur.fetchall()
                result = [
                    {
                        "id": o[0], "created_at": o[1], "feedback": o[2],
                        "receipt": o[3], "bill_amount": o[4], "user": o[5]
                    }
                    for o in orders
                ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@crud_blueprint.route("/users/<phone>/lastlogin", methods=["PUT"])
def update_lastlogin(phone):
    data = request.get_json()
    new_lastlogin = data.get("lastlogin")
    
    if not new_lastlogin:
        return jsonify({"status": "error", "message": "Missing 'lastlogin' field in request."}), 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE users
                    SET lastlogin = %s
                    WHERE phone = %s;
                """, (new_lastlogin, phone))

                if cur.rowcount == 0:
                    return jsonify({"status": "error", "message": "User not found."}), 404

        return jsonify({"status": "success", "message": f"Last login updated for user {phone}."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
@crud_blueprint.route("/orders/<string:phone>", methods=["GET"])
def get_orders_by_phone(phone):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT o.id, o.created_at, o.feedback, o.receipt, o.bill_amount, o.userid
                    FROM orders o
                    JOIN users u ON o.userid = u.phone
                    WHERE u.phone = %s;
                """, (phone,))
                
                orders = cur.fetchall()
                result = [
                    {
                        "id": o[0], "created_at": o[1], "feedback": o[2],
                        "receipt": o[3], "bill_amount": o[4], "user": o[5]
                    }
                    for o in orders
                ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@crud_blueprint.route("/users/exist", methods=["POST"])
def check_user_existence():
    data = request.get_json()
    user_id = data.get("id")
    phone = data.get("phone")

    response, status = user_exists(user_id=user_id, phone=phone)
    return jsonify(response), status



@crud_blueprint.route("/products/categorized", methods=["GET"])
def get_categorized_products():
    result = fetch_and_categorize_products()
    if "status" in result and result["status"] == "error":
        return jsonify(result), 400
    return jsonify(result), 200

@crud_blueprint.route('/sendCatalogueCategory', methods=['POST'])
def post_whatsapp_product_list():
    # Get data from request
    data = request.get_json()
    
    # Extract category and to_number from the request payload
    category = data.get("category")
    to_number = data.get("to_number")
    
    if not category or not to_number:
        return jsonify({"status": "error", "message": "Missing category or to_number"}), 400
    
    # Call the function to send WhatsApp product list
    result = send_whatsapp_product_list(category, to_number)
    
    return jsonify(result)

