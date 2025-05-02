import json
import os
import requests

FACEBOOK_API_URL = "https://graph.facebook.com/v22.0/1595768864475137/products"
ACCESS_TOKEN ="EAAQKF56ZAbJQBO8QjZB1Lmr471oHsunN8bqvophvlHGGt08TrOXrE6nKTUwwTBkfBK2ub9i1ZAZANFHsvPP0g2yyJLcZBxhMrLKH4fzv4UM5EbwzsL9PeS7FdfjSbF3Yo59oVmKoc4FMvwRcyJsc6CPyAPTuOrXlKXYhlcJzOqmK4g0Yx3BxG0Yf2AjuLEvPKBOmsLixQgCCpFiKKF9ZC6eNXDvuNEcst27oIap7CF"


def fetch_and_categorize_products():
    try:
        response = requests.get(
            FACEBOOK_API_URL,
            params={
                "fields": "id,name,retailer_id,description,price,availability",
                "access_token": ACCESS_TOKEN,
                "limit": 25
            }
        )
        data = response.json()

        if "data" not in data:
            raise Exception("Invalid API response format")

        products = data["data"]

        categorized = {
            "vegetables": {},
            "groceries": {},
            "fruits": {}
        }

        for item in products:
            rid = item.get("retailer_id", "").lower()
            product_info = {
                "id": item.get("id"),
                "name": item.get("name"),
                "description": item.get("description"),
                "price": item.get("price"),
                "availability": item.get("availability"),
                "retailer_id": item.get("retailer_id")
            }

            if rid.startswith("veg"):
                categorized["vegetables"][item["retailer_id"]] = product_info
            elif rid.startswith("gr"):
                categorized["groceries"][item["retailer_id"]] = product_info
            elif rid.startswith("fr"):
                categorized["fruits"][item["retailer_id"]] = product_info

        with open("result.json", "w", encoding="utf-8") as f:
            json.dump(categorized, f, ensure_ascii=False, indent=2)

        return categorized

    except Exception as e:
        return {"status": "error", "message": str(e)}


WHATSAPP_API_URL = "https://graph.facebook.com/v22.0/579242655280457/messages"
WHATSAPP_TOKEN = os.getenv("ACCESS_TOKEN")
def load_products_by_category(category: str):
    try:
        with open("result.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get(category, {})
    except Exception as e:
        return {}

def send_whatsapp_product_list(category: str, to_number: str):
    if isinstance(category, list):
        product_items = [{"product_retailer_id": rid} for rid in category]
    else:
        # Otherwise, load from file
        product_dict = load_products_by_category(category)
        if not product_dict:
            return {"status": "error", "message": "Category not found or empty"}
        product_items = [{"product_retailer_id": rid} for rid in product_dict.keys()]
    
    print(product_items)

    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "interactive",
        "interactive": {
            "type": "product_list",
            "header": {
                "type": "text",
                "text": "🛒 eMart Specials"
            },
            "body": {
                "text": "Check out our latest products!"
            },
            "footer": {
                "text": "Tap a product to view more."
            },
            "action": {
                "catalog_id": "1595768864475137",
                "sections": [
                    {
                        "title": "Popular Items",
                        "product_items": product_items
                    }
                ]
            }
        }
    }

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
    return {"status": "success" if response.ok else "error", "response": response.json()}