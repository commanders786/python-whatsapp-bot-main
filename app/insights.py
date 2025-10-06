from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from .crud import get_db_connection  # assuming you have this
from psycopg2.extras import DictCursor
import platform

insights_blueprint = Blueprint("insights", __name__)

@insights_blueprint.route("/orders/insights/orderSummary", methods=["GET"])
def get_orders_insights():
    try:
        # Query params
        userid = request.args.get("userid", None)

        # Calculate last 10 days range
        today = datetime.today().date()
        start_date = today - timedelta(days=9)  # include today

        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                # Build WHERE clause
                where_clauses = ["created_at >= %s"]
                params = [start_date]

                if userid:
                    where_clauses.append("userid = %s")
                    params.append(userid)

                where_clause = " AND ".join(where_clauses)

                # Query to fetch count of orders grouped by date
                query = f"""
                    SELECT DATE(created_at) AS order_date, COUNT(*) AS total_orders
                    FROM orders
                    WHERE {where_clause}
                    GROUP BY order_date
                    ORDER BY order_date ASC;
                """

                cur.execute(query, params)
                results = cur.fetchall()

                # Prepare data for last 10 days (ensure zero counts for missing dates)
                date_counts = {r["order_date"]: r["total_orders"] for r in results}

                categories = []
                counts = []

                # Detect platform-specific formatting
                day_format = "%-d %b" if platform.system() != "Windows" else "%#d %b"

                for i in range(10):
                    date = start_date + timedelta(days=i)
                    formatted_date = date.strftime(day_format)  # Example: 2 Jul
                    categories.append(formatted_date)
                    counts.append(date_counts.get(date, 0))

        # ApexCharts compatible response
        response = {
            "series": [
                {
                    "name": "Orders",
                    "data": counts
                }
            ],
            "categories": categories
        }
        return jsonify(response), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400


@insights_blueprint.route("/orders/insights/saleSummary", methods=["GET"])
def get_orders_insights_sum():
    try:
        # Query params
        userid = request.args.get("userid", None)

        # Calculate last 10 days range
        today = datetime.today().date()
        start_date = today - timedelta(days=9)  # include today

        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                # Build WHERE clause
                where_clauses = ["created_at >= %s"]
                params = [start_date]

                if userid:
                    where_clauses.append("userid = %s")
                    params.append(userid)

                where_clause = " AND ".join(where_clauses)

                # Query to fetch total sales grouped by date
                query = f"""
                    SELECT DATE(created_at) AS order_date, COALESCE(SUM(bill_amount), 0) AS total_sale
                    FROM orders
                    WHERE {where_clause}
                    GROUP BY order_date
                    ORDER BY order_date ASC;
                """

                cur.execute(query, params)
                results = cur.fetchall()

                # Prepare data for last 10 days (ensure zero for missing dates)
                date_sales = {r["order_date"]: r["total_sale"] for r in results}

                categories = []
                sales = []

                # Detect platform-specific formatting
                day_format = "%-d %b" if platform.system() != "Windows" else "%#d %b"

                for i in range(10):
                    date = start_date + timedelta(days=i)
                    formatted_date = date.strftime(day_format)  # Example: 2 Jul
                    categories.append(formatted_date)
                    sales.append(float(date_sales.get(date, 0)))

        # ApexCharts compatible response
        response = {
            "series": [
                {
                    "name": "Sales",
                    "data": sales
                }
            ],
            "categories": categories
        }
        return jsonify(response), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400
