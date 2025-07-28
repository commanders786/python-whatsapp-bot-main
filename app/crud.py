import json
import logging
from flask import Blueprint, request, jsonify,Response
import psycopg2
import queue
from app.services.crud_services import clear_payment_service, de_map_products_service, get_order_details_service, get_order_items_service, get_order_summary_service, get_product_by_retailerid_service, get_products_service, get_products_service_new, get_reciept_service, get_vendor_products_service, get_vendor_service, insert_order, insert_user, insert_vendor_service, map_products_service, update_availability_service, update_order_items_service, update_order_items_service_new, update_price_service, update_vendor_price_service, user_exists
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
                cur.execute("SELECT id, phone, name, lastlogin, language,created_at FROM users order by lastlogin desc;")
                users = cur.fetchall()
                result = [
                    {"id": u[0], "phone": u[1], "name": u[2], "lastlogin": u[3], "language": u[4],"created_at":u[5]}
                    for u in users
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
    

@crud_blueprint.route("/users/exist", methods=["POST"])
def check_user_existence():
    data = request.get_json()
    user_id = data.get("id")
    phone = data.get("phone")

    response, status = user_exists(user_id=user_id, phone=phone)
    return jsonify(response), status

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
                cur.execute("SELECT id, created_at, feedback, receipt, bill_amount, userid,status,is_offline FROM orders order by created_at desc;")
                orders = cur.fetchall()
                result = [
                    {
                        "id": o[0], "created_at": o[1], "feedback": o[2],
                        "receipt": o[3], "bill_amount": o[4], "user": o[5],"status":o[6],"is_offline":o[7]
                    }
                    for o in orders
                ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    

@crud_blueprint.route("/orders/<int:order_id>", methods=["PUT"])
def update_order_status(order_id):
    try:
        data = request.get_json()
        status = data.get("status")
        
        if not status or status not in ["pending", "delivered"]:
            return jsonify({"status": "error", "message": "Invalid or missing status. Must be 'pending' or 'delivered'"}), 400
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE orders SET status = %s WHERE id = %s::varchar RETURNING id, status;",
                    (status, str(order_id))
                )
                updated_order = cur.fetchone()
                
                if not updated_order:
                    return jsonify({"status": "error", "message": "Order not found"}), 404
                    
                conn.commit()
                return jsonify({
                    "status": "success",
                    "order": {
                        "id": updated_order[0],
                        "status": updated_order[1]
                    }
                }), 200
                
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



@crud_blueprint.route("/order-items/update", methods=["POST"])
def update_order_items():
    try:
        data = request.get_json()
        order_id = data.get("order_id")
        items = data.get("items", [])

        if not order_id or not items:
            return jsonify({"error": "Missing order_id or items"}), 400

        success, message = update_order_items_service(order_id, items)
        if success:
            return jsonify({"message": message}), 200
        else:
            return jsonify({"error": message}), 500

    except Exception as e:
        logging.exception("An error occurred while updating order items")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

    

@crud_blueprint.route("/order-items/all", methods=["GET"])
def get_order_items():
    order_id = request.args.get("order_id")
    product_id = request.args.get("product_id")
    
    response, status = get_order_items_service(order_id, product_id)
    return jsonify(response), status



@crud_blueprint.route("/orders/summary", methods=["GET"])
def get_order_summary():
    vendor = request.args.get("vendor")
    response, status = get_order_summary_service(vendor)
    return jsonify(response), status



@crud_blueprint.route("/reciept", methods=["GET"])
def get_reciept():
    order_id = request.args.get("order_id")
    

    response, status = get_reciept_service(order_id)
    return jsonify(response), status
# ------------------ Products ------------------


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



@crud_blueprint.route("/products", methods=["GET"])
def get_products():
    product_ids_param = request.args.get("product_ids")
    product_ids = product_ids_param.split(",") if product_ids_param else None

    response, status = get_products_service(product_ids)
    return jsonify(response), status





@crud_blueprint.route("/product-by-retailerid", methods=["GET"])
def get_product_by_retailerid():
    retailer_id = request.args.get("retailer_id")
    if not retailer_id:
        return jsonify({"status": "error", "message": "retailer_id is required"}), 400

    result, status_code = get_product_by_retailerid_service(retailer_id)
    return jsonify(result), status_code



@crud_blueprint.route("/updatePrice", methods=["POST"])
def update_price():
    data = request.get_json()
    price = data.get("price")
    product_id=data.get("id")

    

    success, message = update_price_service(product_id, price)
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 500
    

@crud_blueprint.route("/updateStock", methods=["POST"])
def update_stock():
    data = request.get_json()
    availability = data.get("availability")
    product_id=data.get("id")

    

    success, message = update_availability_service(product_id, availability)
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 500
    



@crud_blueprint.route("/productsNew", methods=["POST"])
def get_products_new():
    data = request.get_json()
    
    response, status = get_products_service_new(data)
    return jsonify(response), status



@crud_blueprint.route("/update-order-items", methods=["POST"])
def update_order_items_new():
    data = request.get_json()
    return update_order_items_service_new(data)

@crud_blueprint.route("/order-details", methods=["POST"])
def get_order_details():
    data = request.get_json()
    return get_order_details_service(data)






# ------------------ Vendors ------------------



@crud_blueprint.route("/vendors", methods=["GET"])
def get_vendors():
    response, status = get_vendor_service()
    return jsonify(response), status



@crud_blueprint.route("/mapProducts", methods=["POST"]) 
def mapProducts():
    data = request.get_json()
    return map_products_service(data) 


@crud_blueprint.route("/deMapProducts", methods=["POST"]) 
def deMapProducts():
    data = request.get_json()
    return de_map_products_service(data) 





@crud_blueprint.route("/vendorsproducts", methods=["POST"])
def get_vendor_products():
    data = request.get_json()
    
    return get_vendor_products_service(data) 


@crud_blueprint.route("/vendors", methods=["POST"])
def insert_vendor():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        name = data.get("name")
        product_type = data.get("product_type")

        if not name or not product_type:
            return jsonify({"error": "Missing required fields: name and product_type"}), 400

        response, status = insert_vendor_service(data)
        return jsonify(response), status

    except ValueError:
        return jsonify({"error": "Invalid JSON format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@crud_blueprint.route("/update-vendor-price", methods=["POST"])
def update_vendor_price():
    data = request.get_json()
    return update_vendor_price_service(data)


# ------------------ Accounts ------------------

# @crud_blueprint.route("/accounts", methods=["POST"])
# def get_vendor_accounts():
#     data = request.get_json()
    
#     return get_vendor_accounts_service(data) 



@crud_blueprint.route("/clearPayment", methods=["POST"])
def clear_payment():
    data = request.get_json()
    
    return clear_payment_service(data) 


# clients=[]
# @crud_blueprint.get("/events")
# def sse_stream():
#     def event_stream(q):
#         try:
#             while True:
#                 data = q.get()
#                 yield f"data: {json.dumps(data)}\n\n"
#         except GeneratorExit:
#             print("Client disconnected")

#     q = queue.Queue()
#     clients.append(q)
#     return Response(event_stream(q), mimetype="text/event-stream")
