import json
import logging
from flask import Blueprint, request, jsonify,Response
import psycopg2
import queue
from app.services.cloud_apis import send_feedback_buttons
from app.services.crud_services import clear_payment_service, de_map_products_service, get_order_details_service, get_order_items_service, get_order_summary_service, get_product_by_retailerid_service, get_products_service, get_products_service_new, get_reciept_service, get_vendor_products_service, get_vendor_service, insert_order, insert_user, insert_vendor_service, map_products_service, update_availability_service, update_order_items_service, update_order_items_service_new, update_price_service, update_product_details_service, update_vendor_price_service, user_exists, vendor_account_updation_service
from app.services.product_service import fetch_and_categorize_products, send_whatsapp_product_list
from datetime import datetime, timedelta

crud_blueprint = Blueprint("crud", __name__)

# Connection config - You can later refactor this into a separate config file
DB_CONFIG = {
    "user": "postgres.dmepnqgumjlvwaqnaybp",
    "password": "Kamsaf@786",
    "host": "aws-0-ap-south-1.pooler.supabase.com",
    "port": "6543",
    "dbname": "postgres"
}

from contextlib import contextmanager
from psycopg2 import pool

# Connection pool
connection_pool = None


def reset_connection_pool():
    """
    Reset the connection pool completely. Use in case of persistent errors.
    """
    global connection_pool
    if connection_pool:
        connection_pool.closeall()
    connection_pool = None
    init_connection_pool()

    print("♻️ Connection pool reset")
    


def init_connection_pool():
    global connection_pool
    if connection_pool is None:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,  # Adjust based on your DB limits
            **DB_CONFIG
        )

@contextmanager
def get_db_connection():
    init_connection_pool()
    conn = connection_pool.getconn()
    try:
        yield conn
        conn.commit()  # commit successful queries
    except Exception as e:
        conn.rollback()  # rollback on any exception
        print(f"❌ DB error, rolled back transaction: {e}")
        raise
    finally:
        connection_pool.putconn(conn)

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
                print(f"Executed UPDATE for phone={phone} with lastlogin={new_lastlogin}")  # Debug
                conn.commit()

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
        # Get query params
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        search = request.args.get("search", "")
        feedback = request.args.get("feedback", "")
        start_date = request.args.get("start_date", "")
        end_date = request.args.get("end_date", "")
        offset = (page - 1) * per_page

        print(f"Received query params: page={page}, per_page={per_page}, search={search}, feedback={feedback}, start_date={start_date}, end_date={end_date}")  # Debug

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Build the WHERE clause for filtering
                where_clauses = []
                params = []

                if search:
                    where_clauses.append("(id ILIKE %s OR userid ILIKE %s)")
                    params.extend([f"%{search}%", f"%{search}%"])
                if feedback:
                    where_clauses.append("feedback = %s")
                    params.append(feedback)
                if start_date:
                    where_clauses.append("created_at >= %s")
                    params.append(start_date)
                if end_date:
                    # Extend end_date to end of day
                    try:
                        end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")
                        end_date_dt = end_date_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
                        where_clauses.append("created_at <= %s")
                        params.append(end_date_dt)
                    except ValueError:
                        return jsonify({"status": "error", "message": "Invalid end_date format"}), 400

                where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

                # Fetch total count with filters
                cur.execute(f"SELECT COUNT(*) FROM orders WHERE {where_clause};", params)
                total_count = cur.fetchone()[0]

                # Fetch total sales (sum of bill_amount) with filters
                cur.execute(f"SELECT COALESCE(SUM(bill_amount), 0) FROM orders WHERE {where_clause};", params)
                total_sales = float(cur.fetchone()[0])

                # Fetch paginated data with filters
                query = f"""
                    SELECT id, created_at, feedback, receipt, COALESCE(bill_amount, 0), userid, status, is_offline
                    FROM orders
                    WHERE {where_clause}
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s;
                """
                print(f"Executing query: {query} with params: {params + [per_page, offset]}")  # Debug
                params.extend([per_page, offset])
                cur.execute(query, params)
                orders = cur.fetchall()

                result = [
                    {
                        "id": o[0],
                        "created_at": o[1].isoformat(),
                        "feedback": o[2],
                        "receipt": o[3],
                        "bill_amount": float(o[4]),
                        "user": o[5],
                        "status": o[6],
                        "is_offline": o[7]
                    }
                    for o in orders
                ]

        response = {
            "page": page,
            "per_page": per_page,
            "total": total_count,
            "total_sales": total_sales,
            "total_pages": (total_count + per_page - 1) // per_page,
            "data": result
        }
        return jsonify(response), 200

    except Exception as e:
        print(f"Error: {str(e)}")  # Debug
        return jsonify({"status": "error", "message": str(e)}), 400
    
@crud_blueprint.route("/orders/<int:order_id>", methods=["PUT"])
def update_order_status(order_id):
    try:
        data = request.get_json()
        status = data.get("status")
        
        if not status or status not in ["pending", "delivered","cancelled","picked up"]:
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
                # 2️⃣ Fetch userid (phone number) for this order
                cur.execute("SELECT userid FROM orders WHERE id = %s::varchar", (str(order_id),))
                user_row = cur.fetchone()
                user_phone = user_row[0] if user_row else None

                conn.commit()

        # 3️⃣ If delivered, trigger WhatsApp feedback message
        if status == "delivered" and user_phone:
            try:
                send_feedback_buttons(user_phone, language="ml")
            except Exception as send_err:
                print(f"⚠️ Failed to send feedback message: {send_err}")
                    
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
    
  
    return get_products_service_new(data)



@crud_blueprint.route("/update-order-items", methods=["POST"])
def update_order_items_new():
    data = request.get_json()
    return update_order_items_service_new(data)

@crud_blueprint.route("/order-details", methods=["POST"])
def get_order_details():
    data = request.get_json()
    return get_order_details_service(data)


@crud_blueprint.route("/update-product-meta", methods=["POST"])
def update_product_details():
    data = request.get_json()
    return update_product_details_service(data)






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


@crud_blueprint.route("/vendorAmountUpdation", methods=["POST"])
def vendor_amount_updation():
    data = request.get_json()
    
    return vendor_account_updation_service(data) 


@crud_blueprint.route("/clearPayment", methods=["POST"])
def clear_payment():
    data = request.get_json()
    
    return clear_payment_service(data) 


clients=[]
@crud_blueprint.get("/events")
def sse_stream():
    def event_stream(q):
        try:
            while True:
                data = q.get()
                yield f"data: {json.dumps(data)}\n\n"
        except GeneratorExit:
            print("Client disconnected")

    q = queue.Queue()
    clients.append(q)
    return Response(event_stream(q), mimetype="text/event-stream")
