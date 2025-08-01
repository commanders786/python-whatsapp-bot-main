from datetime import datetime, timezone
import json
import logging

from app.utils.sse import get_clients

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from flask import jsonify
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
                is_offline = data.get('is_offline', False)
                # Insert order without feedback
                cur.execute("""
                    INSERT INTO orders (id, receipt, bill_amount, userid, created_at, is_offline)
                    VALUES (%s, %s, %s, %s, NOW(), %s);
                """, (order_id, data['receipt'], data['bill_amount'], data['userid'], is_offline))

            for q in get_clients():
               q.put({
            "message": "New order created",
            "order": order_id
        })

        return {"status": "success", "message": "Order added.", "order_id": order_id}, 201
    except Exception as e:
        return {"status": "error", "message": str(e)}, 400


def update_order_items_service(orderId, items):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Optionally delete existing items for that order_id
                # cur.execute("DELETE FROM order_items WHERE order_items.orderId = %s", (orderId,))

                # Insert new items
                for item in items:
                    cur.execute("""
                        INSERT INTO order_items ( order_id, product_id, qty, total)
                        VALUES (%s, %s, %s, %s);
                    """, (
                       
                        orderId,
                        item['product_retailer_id'],
                        item['quantity'],
                        item['item_price'] * item['quantity']  # Total = unit * qty
                    ))
        logging.info("order items updated")
        return {"status": "success", "message": "Order items updated."}, 200

    except Exception as e:
        logging.info(e)
        return {"status": "error", "message": str(e)}, 500
    
def get_order_items_service(order_id=None, product_id=None):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                query = """
                    SELECT order_id, product_id, qty, total
                    FROM order_items
                """
                params = []

                # Apply filters
                if order_id and product_id:
                    query += " WHERE order_id = %s AND product_id LIKE %s"
                    params.extend([order_id, product_id[:2] + '%'])
                elif order_id:
                    query += " WHERE order_id = %s"
                    params.append(order_id)

                query += " ORDER BY order_id"

                cur.execute(query, tuple(params))
                rows = cur.fetchall()

                result = [
                    {
                        "order_id": row[0],
                        "product_id": row[1],
                        "quantity": row[2],
                        "total": row[3]
                    } for row in rows
                ]

        return {"status": "success", "data": result}, 200

    except Exception as e:
        logging.error("Error fetching order items: %s", str(e))
        return {"status": "error", "message": str(e)}, 500


def get_order_summary_service(vendor=None):
    try:

       
        if vendor:
                if len(vendor)>3:
                    vendor=tuple(vendor.split(","))
                    query=f"""
                    SELECT 
                        o.id AS order_id,
                        COUNT(oi.product_id) AS item_count,
                        o.created_at,
                        o.status
                    FROM orders o
                    JOIN order_items oi ON o.id = oi.order_id
                    where oi.product_id in {vendor}
                    GROUP BY o.id, o.created_at, o.status
                    ORDER BY o.created_at DESC
                    LIMIT 100;
                """
                else:
                   query=f"""
                      SELECT 
                        o.id AS order_id,
                        COUNT(oi.product_id) AS item_count,
                        o.created_at,
                        o.status
                    FROM orders o
                    JOIN order_items oi ON o.id = oi.order_id
                    where oi.product_id like '{vendor}%'
                    GROUP BY o.id, o.created_at, o.status
                    ORDER BY o.created_at DESC
                    LIMIT 100;
                """
        else:
             query=f"""
                    SELECT 
                        o.id AS order_id,
                        COUNT(oi.product_id) AS item_count,
                        o.created_at,
                        o.status
                    FROM orders o
                    JOIN order_items oi ON o.id = oi.order_id
                    GROUP BY o.id, o.created_at, o.status
                    ORDER BY o.created_at DESC
                    LIMIT 100;
                """
             
        print(query)
        with get_db_connection() as conn:
            
            with conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()

                result = [
                    {
                        "order_id": row[0],
                        "item_count": row[1],
                        "created_at": row[2],
                        "status": row[3]
                    } for row in rows
                ]

        return {"status": "success", "data": result}, 200

    except Exception as e:
        logging.error("Error fetching order summary: %s", str(e))
        return {"status": "error", "message": str(e)}, 500



import requests

ACCESS_TOKEN = "EAAQKF56ZAbJQBO3eHvyzD8AERlnLM7hAvtAIZCcSYubLA7JqPq7iv2NGlzlgDfX1DnJ9CJl9ZANyHdiHYNztdvAjf2C4XKWXFMBCjqTagNJDV4VYV59VhzLQ76kZBjrVP3XDsa2UeqBmT9lr01zgImVXPcmeDsyf6KXOaDk61yFzMKS5BkFZBhDX4tsMfuJ4ZA5QZDZD"
GRAPH_API_URL = "https://graph.facebook.com/v22.0/1595768864475137/products"
FIELDS = "name,retailer_id,price,size,image_url,sale_price"

def get_product_by_retailerid_service(retailer_id):
    try:
        response = requests.get(
            GRAPH_API_URL,
            params={
                "fields": FIELDS,
                "access_token": ACCESS_TOKEN,
                "limit": 120
            }
        )
        response.raise_for_status()
        data = response.json().get("data", [])

        # Find matching product
        product = next((item for item in data if item.get("retailer_id") == retailer_id), None)

        if product:
            return {
                "status": "success",
                "product": {
                    "name": product.get("name"),
                    "price": product.get("price"),
                    "image_url": product.get("image_url")
                }
            }, 200
        else:
            return {"status": "not_found", "message": "Product not found for given retailer_id"}, 404

    except Exception as e:
        return {"status": "error", "message": str(e)}, 500



def get_products_service(product_ids=None):
    try:
        with open("result.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        if product_ids:
            # Flat lookup: search across all categories
            filtered_products = {}
            for category_items in data.values():
                for product in category_items.values():
                    if product["retailer_id"] in product_ids:
                        filtered_products[product["retailer_id"]] = product["name"]
            return filtered_products, 200

        # If no product_ids, return full category-wise data
        result = {}
        for category, items in data.items():
            result[category] = []
            for product in items.values():
                product_data = {
                    "id": product.get("id"),
                    "name": product.get("name"),
                    "description": product.get("description"),
                    "price": product.get("price"),
                    "sale_price": product.get("sale_price"),
                    "availability": product.get("availability"),
                    "retailer_id": product.get("retailer_id"),
                }
                result[category].append(product_data)

        return result, 200

    except Exception as e:
        print("Error while loading products:", e)
        return {"error": "Internal Server Error"}, 500
    
def get_reciept_service(order_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                query = """
                    SELECT receipt
                    FROM orders
                    WHERE id= %s
                """
                cur.execute(query, (order_id,))
                row = cur.fetchone()

                if row:
                    return {"order_id": order_id, "reciept": row[0]}, 200
                else:
                    return {"error": "Order not found"}, 404

    except Exception as e:
        print("Error while loading reciept:", e)
        return {"error": "Internal Server Error"}, 500


def update_price_service(item_id, price):
    """
    Update the price for a WhatsApp Business API item using the Facebook Graph API.
    
    Args:
        item_id (str): The ID of the item (e.g., '10071002672936807').
        price (str): The price to set (e.g., '4200').
        access_token (str): The Bearer token for authentication.
    
    Returns:
        dict: The API response as a JSON object, or None if the request fails.
    """
    url = f"https://graph.facebook.com/v22.0/{item_id}"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "price": price
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raises an HTTPError for 4xx/5xx responses
        
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.json()}")
        return {"message":"success"}, 200
        # return response.json()
    
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response text: {response.text}")
        return response.text,500
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        return req_err,500
    except ValueError as json_err:
        print(f"JSON decode error: {json_err}")
        print(f"Response text: {response.text}")
        return response.text,500
    

def update_availability_service(item_id, availability):
    """
    Update the availability for a WhatsApp Business API item using the Facebook Graph API.
    
    Args:
        item_id (str): The ID of the item (e.g., '9395913967197870').
        availability (str): The availability to set (e.g., 'out of stock').
        access_token (str): The Bearer token for authentication.
    
    Returns:
        dict: The API response as a JSON object, or None if the request fails.
    """
    url = f"https://graph.facebook.com/v22.0/{item_id}"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "availability": availability
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raises an HTTPError for 4xx/5xx responses
        
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.json()}")
        
        return {"message":"success"}, 200
        # return response.json()
    
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response text: {response.text}")
        return response.text,500
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        return req_err,500
    except ValueError as json_err:
        print(f"JSON decode error: {json_err}")
        print(f"Response text: {response.text}")
        return response.text,500
    





def update_user_lastlogin(user_id):
    try:
        # Get current GMT/UTC time
        now_gmt = datetime.now(timezone.utc)

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE users
                    SET lastlogin = %s
                    WHERE id = %s;
                """, (now_gmt, user_id))
                if cur.rowcount == 0:
                    
                    
                    logging.warning(f"User not found for ID: {user_id}")
                    return
        logging.info("last login updated...")
        
      
    except Exception as e:
        logging.error(f"Failed to update last login for user {user_id}: {e}")


def get_vendor_products(user):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT vendor_products FROM role_users WHERE username = %s", (user,))
    row = cur.fetchone()
    cur.close()
    conn.close()

   

    
    return {"products": row[0] ,"status": 200}

def get_vendor_service():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
       SELECT v.id,username,shop_name,phone FROM role_users r JOIN vendors v ON r.phone = v.id;
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        # Optional: convert to list of dicts
        columns = [desc[0] for desc in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]

        return result, 200

    except Exception as e:
        return {"error": str(e)}, 500

    finally:
        # cursor.close()
        conn.close()


import pandas as pd

def get_products_service_new(data):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        vendor = data.get("vendorId")
        type = data.get("type")
        type = True if type == "paid" else False

        # Step 1: Check if vendor exists and its product type
        vendor_query = """
            SELECT product_type, commision FROM vendors WHERE id = %s
        """
        cursor.execute(vendor_query, (vendor,))
        vendor_result = cursor.fetchone()

        if not vendor_result:
            return {"error": "Vendor not found"}, 404

        product_type, commision = vendor_result

        # Step 2: Choose query based on product type
        if product_type == 'multi':
            order_query = """
                SELECT 
                    oi.order_id,
                    SUM(oi.total) AS bill_amount
                FROM orders o
                JOIN order_items oi ON o.id = oi.order_id
                JOIN products p ON p.retailer_id = oi.product_id
                JOIN vendors v ON v.id = p.vendor_id
                WHERE 
                    oi.payment_done = %s AND 
                    oi.is_cancelled = FALSE AND 
                    v.id = %s
                GROUP BY oi.order_id
                ORDER BY MAX(o.created_at) DESC
            """
            cursor.execute(order_query, (type, vendor))
        else:
            order_query = """
                SELECT 
                    oi.order_id,
                    SUM(oi.total) AS bill_amount
                FROM orders o
                JOIN order_items oi ON o.id = oi.order_id
                WHERE 
                    oi.product_id LIKE %s AND 
                    oi.payment_done = %s AND 
                    oi.is_cancelled = FALSE
                GROUP BY oi.order_id
                ORDER BY MAX(o.created_at) DESC
            """
            cursor.execute(order_query, (f"%{product_type}%", type))

        order_rows = cursor.fetchall()
        

        # Step 3: Use pandas to aggregate and format result
        df = pd.DataFrame(order_rows, columns=['order_id', 'bill_amount'])

        if df.empty:
            return {
                "orders": [],
                "pending_amount" if type == 0 else "cleared_amount": 0
            }, 200

        df['bill_amount'] = pd.to_numeric(df['bill_amount'])
        total_pending = int(df['bill_amount'].sum())
        orders = df.to_dict(orient='records')
        
        
        if commision and not type:
            payable=total_pending-(total_pending*commision/100)
        else:
            payable=None

        
        response = {
            "orders": orders,
            "pending_amount" if type == 0 else "cleared_amount": total_pending,
            "commision":commision ,
            "payable":payable
            
        }

        return response, 200

    except Exception as e:
        print(e)
        return {"error": str(e)}, 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_vendor_products_service(data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        vendor_id = data.get("vendorId")

        # Step 1: Check if vendor exists
        vendor_query = """
            SELECT product_type FROM vendors WHERE id = %s
        """
        cursor.execute(vendor_query, (vendor_id,))
        vendor_result = cursor.fetchone()

        if not vendor_result:
            return jsonify({"error": "Vendor not found"}), 404

        # Step 2: Get products by vendor
        order_query = """
            SELECT 
                p.p_id,p.retailer_id, p.name, p.vendors_price,p.percentage_on_category
            FROM products p
            JOIN vendors v ON v.id = p.vendor_id
            WHERE v.id = %s
        """
        cursor.execute(order_query, (vendor_id,))
        order_rows = cursor.fetchall()

        # Step 3: Format the result
        products = [
            {
                "id": row[0],
                "retailer_id": row[1],
                "name": row[2],
                "vendors_price": row[3],
                "is_percentage":row[4]
            }
            for row in order_rows
        ]

        return jsonify(products), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


def update_order_items_service_new(data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        order_id = data.get("order_id")
        items = data.get("items", [])

        if not order_id:
            return jsonify({"error": "Missing order_id"}), 400

        for item in items:
            product_id = item.get("product_id")
            action = item.get("action")

            if not product_id or not action:
                continue  # Skip invalid item

            if action == "insert":
                qty = item.get("qty", 1)
                vendor_price = item.get("vendor_price", 0)
                cursor.execute("""
                    INSERT INTO order_items (order_id, product_id, qty, vendor_price)
                    VALUES (%s, %s, %s, %s)
                """, (order_id, product_id, qty, vendor_price))

            elif action == "update":
                qty = item.get("qty")
                vendor_price = item.get("vendor_price")
                cursor.execute("""
                    UPDATE order_items
                    SET qty = %s, vendor_price = %s
                    WHERE order_id = %s AND product_id = %s
                """, (qty, vendor_price, order_id, product_id))

            elif action == "delete":
                cursor.execute("""
                    DELETE FROM order_items
                    WHERE order_id = %s AND product_id = %s
                """, (order_id, product_id))

        conn.commit()
        return jsonify({"message": "Order items updated successfully"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        

def get_order_details_service(data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        order_id = data.get("order_id")

        if not order_id:
            return jsonify({"error": "Missing order_id"}), 400

        # Step 1: Get order info
        order_query = """
            SELECT id, userid, bill_amount, status, created_at, feedback, receipt
            FROM orders
            WHERE id = %s
        """
        cursor.execute(order_query, (order_id,))
        order = cursor.fetchone()

        if not order:
            return jsonify({"error": "Order not found"}), 404

        order_info = {
            "id": order[0],
            "userid": order[1],
            "bill_amount": order[2],
            "status": order[3],
            "created_at": order[4],
            "feedback": order[5],
            "receipt": order[6]
        }

        # Step 2: Get order items
        items_query = """
            SELECT product_id, qty, vendor_price, total, unit, payment_done, is_cancelled
            FROM order_items
            WHERE order_id = %s
        """
        cursor.execute(items_query, (order_id,))
        items = cursor.fetchall()

        item_list = [
            {
                "product_id": i[0],
                "qty": i[1],
                "vendor_price": i[2],
                "total": i[3],
                "unit": i[4],
                "payment_done": i[5],
                "is_cancelled": i[6]
            }
            for i in items
        ]

        return jsonify({
            "order": order_info,
            "items": item_list
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


def map_products_service(data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Extract relevant fields from the incoming data
        name = data.get("name")
        vendor_id = data.get("vendor_id")
        category = data.get("category")
        percentage_on_category = data.get("percentage_on_category")
        vendors_price = data.get("vendors_price")
        retailer_id = data.get("retailer_id")
        p_id = data.get("p_id")

        insert_query = """
            INSERT INTO products (
                name,
                vendor_id,
                category,
                percentage_on_category,
                vendors_price,
                retailer_id,
                p_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(insert_query, (
            name,
            vendor_id,
            category,
            percentage_on_category,
            vendors_price,
            retailer_id,
            p_id
        ))

        conn.commit()
        return {"message": "Product mapped successfully"}, 201

    except Exception as e:
        return {"error": str(e)}, 500

    finally:
        conn.close()


def de_map_products_service(data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Extract relevant fields from the incoming data
      
        vendor_id = data.get("vendor_id")
        
        
        retailer_id = data.get("retailer_id")
       

        delete_query = """
            delete from products
                   where retailer_id=%s and vendor_id=%s
        """

        cursor.execute(delete_query, (retailer_id,vendor_id,))

        conn.commit()
        return {"message": "Product removed successfully"}, 201

    except Exception as e:
        return {"error": str(e)}, 500

    finally:
        conn.close()

def insert_vendor_service(data):
    conn = None
    cursor = None
    try:
        logger.debug("Attempting to insert vendor with data: %s", data)
        conn = get_db_connection()
        cursor = conn.cursor()

        id = data.get("id")
        name = data.get("name")
        product_type = data.get("product_type")

        if not all([id, name, product_type]):
            logger.warning("Missing required fields: id=%s, name=%s, product_type=%s", id, name, product_type)
            return {"error": "Missing required fields: id, name, and product_type"}, 400

        # Insert query
        insert_query = """
            INSERT INTO vendors (id, shop_name, product_type, created_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id, shop_name, product_type, created_at
        """
        current_time = datetime.now()
        cursor.execute(insert_query, (id, name, product_type, current_time))

        vendor_row = cursor.fetchone()
        conn.commit()

        if not vendor_row:
            logger.error("No vendor row returned after insert")
            return {"error": "Failed to insert vendor"}, 500

        response = {
            "id": vendor_row[0],
            "name": vendor_row[1],
            "product_type": vendor_row[2],
            "created_at": vendor_row[3].isoformat()
        }
        logger.info("Successfully inserted vendor: %s", response)
        return response, 201

    except psycopg2.IntegrityError as e:
        conn.rollback()
        logger.error("IntegrityError during vendor insert: %s", str(e))
        return {"error": f"Database error: {str(e)}"}, 400
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error("Unexpected error during vendor insert: %s", str(e))
        return {"error": str(e)}, 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        logger.debug("Database connection closed")





def clear_payment_service(data):

    vendor_id = data.get("vendorId")
    transaction_id = data.get("transactionId")
    description = data.get("description")

    if not vendor_id or not transaction_id or not description:
        return jsonify({
            "error": "vendorId, transactionId, and description are required"
        }), 400

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Step 1: Get vendor product type
        cursor.execute("SELECT product_type FROM vendors WHERE id = %s", (vendor_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"error": "Vendor not found"}), 404

        product_type = result[0]

        # Step 2: Get unpaid order_ids
        if product_type == 'multi':
            query = """
                SELECT oi.order_id, SUM(oi.total) AS bill_amount
                FROM orders o
                JOIN order_items oi ON o.id = oi.order_id
                JOIN products p ON p.retailer_id = oi.product_id
                JOIN vendors v ON v.id = p.vendor_id
                WHERE 
                    oi.payment_done = FALSE AND 
                    oi.is_cancelled = FALSE AND 
                    v.id = %s
                GROUP BY oi.order_id
                ORDER BY MAX(o.created_at) DESC
            """
            cursor.execute(query, (vendor_id,))
        else:
            query = """
                SELECT oi.order_id, SUM(oi.total) AS bill_amount
                FROM orders o
                JOIN order_items oi ON o.id = oi.order_id
                WHERE 
                    oi.product_id LIKE %s AND 
                    oi.payment_done = FALSE AND 
                    oi.is_cancelled = FALSE
                GROUP BY oi.order_id
                ORDER BY MAX(o.created_at) DESC
            """
            cursor.execute(query, (f"%{product_type}%",))

        order_rows = cursor.fetchall()
        if not order_rows:
            return jsonify({"message": "No unpaid orders found"}), 200

        order_ids = [row[0] for row in order_rows]
        total_amount = sum([int(row[1]) for row in order_rows])

        # Step 3: Insert into transactions table
        insert_tx = """
            INSERT INTO transactions (transaction_id, amount, description)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_tx, (transaction_id, total_amount, description))

        # Step 4: Update order_items
        update_items = """
            UPDATE order_items
            SET payment_done = TRUE,
                transaction_id = %s
            WHERE order_id = ANY(%s)
              AND is_cancelled = FALSE
        """
        cursor.execute(update_items, (transaction_id, order_ids))

        conn.commit()

        return jsonify({
            "message": "Payment recorded and orders updated",
            "transaction_id": transaction_id,
            "order_ids": order_ids,
            "total_amount": total_amount
        }), 200

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def update_vendor_price_service(data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        retailer_id = data.get("retailer_id")
        vendor_price = data.get("vendor_price")
        commission = data.get("commision")
        vendor_id = data.get("vendor_id")

        if not retailer_id:
            return jsonify({"error": "Missing retailer_id"}), 400

        # When commission is True, set vendors_price to NULL in products and is_percentage True in vendors
        if commission is True:
            update_products_query = """
                UPDATE products
                SET vendors_price = NULL,
                percentage_on_category = TRUE
                WHERE retailer_id = %s and vendor_id= %s
            """
          
            cursor.execute(update_products_query, (retailer_id,vendor_id))
          
        
        else:
            if vendor_price is None:
                return jsonify({"error": "Missing vendor_price"}), 400

            update_products_query = """
                UPDATE products
                SET vendors_price = %s,
                 percentage_on_category = FALSE
                WHERE retailer_id = %s and vendor_id= %s
            """
         
            cursor.execute(update_products_query, (vendor_price, retailer_id,vendor_id))
            

        conn.commit()

        return jsonify({"message": "Vendor price updated successfully"}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()




def vendor_account_updation_service(data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        order_id = data.get("order_id")
        vendor_id = data.get("vendor_id")

        if order_id:
            items_query = '''
                SELECT orders.id, order_items.product_id, order_items.qty, products.vendors_price
                FROM order_items
                JOIN orders ON order_items.order_id = orders.id
                JOIN products ON products.retailer_id = order_items.product_id
                WHERE orders.id = %s
                AND products.percentage_on_category = FALSE;
            '''
            cursor.execute(items_query, (order_id,))
            items = cursor.fetchall()

            for i in items:
                vendor_amount = i[2] * i[3] if i[3] else 0.0  # handle None vendors_price
                vendor_amount_update_query = '''
                    UPDATE order_items
                    SET vendor_price = %s
                    WHERE order_id = %s AND product_id = %s
                '''
                cursor.execute(vendor_amount_update_query, (vendor_amount, order_id, i[1]))

        if vendor_id:
            # TODO: Add vendor-specific logic
            pass

        conn.commit()
        return {"message": "Vendor price updated successfully"}, 201

    except Exception as e:
        return {"error": str(e)}, 500

    finally:
        conn.close()

