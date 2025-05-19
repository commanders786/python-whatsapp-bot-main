import json
import logging
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


def get_order_summary_service():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
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
                """)
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

ACCESS_TOKEN = "EAAQKF56ZAbJQBO8QjZB1Lmr471oHsunN8bqvophvlHGGt08TrOXrE6nKTUwwTBkfBK2ub9i1ZAZANFHsvPP0g2yyJLcZBxhMrLKH4fzv4UM5EbwzsL9PeS7FdfjSbF3Yo59oVmKoc4FMvwRcyJsc6CPyAPTuOrXlKXYhlcJzOqmK4g0Yx3BxG0Yf2AjuLEvPKBOmsLixQgCCpFiKKF9ZC6eNXDvuNEcst27oIap7CF"
GRAPH_API_URL = "https://graph.facebook.com/v22.0/1595768864475137/products"
FIELDS = "name,retailer_id,price,size,image_url"

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
                    "availability": product.get("availability")
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