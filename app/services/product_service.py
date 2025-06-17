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
                "fields": "id,name,retailer_id,description,price,brand,pattern,availability,sale_price",
                "access_token": ACCESS_TOKEN,
                "limit": 300
            }
        )
        data = response.json()

        if "data" not in data:
            raise Exception("Invalid API response format")

        products = data["data"]

        categorized = {
            "vegetables": {},
            "oth": {},
            "fruits": {},
            "meat":{},
            "fish":{},
            "bakeries":{},
              "food":{},
              "general":{},
               "snacks":{},

        }

        restaurants={}

        for item in products:
            rid = item.get("retailer_id", "").lower()
            product_info = {
                "id": item.get("id"),
                "name": item.get("name"),
                "description": item.get("description"),
                "price": item.get("price"),
                "pattern": item.get("pattern") or item.get("brand"),
                "unit":item.get("size"),
                "retailer_id": item.get("retailer_id"),
                "availability": item.get("availability"),
                "sale_price":item.get("sale_price"),
            }

            if rid.startswith("veg"):
                categorized["vegetables"][item["retailer_id"]] = product_info
            elif rid.startswith("gr"):
                categorized["oth"][item["retailer_id"]] = product_info
            elif rid.startswith("fr"):
                categorized["fruits"][item["retailer_id"]] = product_info
            elif rid.startswith("sn"):
                categorized["snacks"][item["retailer_id"]] = product_info
            elif rid.startswith("bk"):
                categorized["bakeries"][item["retailer_id"]] = product_info
            elif rid.startswith("ch") or rid.startswith("kd") or rid.startswith("wp") or rid.startswith("sk"):
                categorized["meat"][item["retailer_id"]] = product_info
            elif rid.startswith("fs"):
                categorized["fish"][item["retailer_id"]] = product_info
            elif rid.startswith("gn"):
                categorized["general"][item["retailer_id"]] = product_info
            elif rid.startswith("rf"):
                categorized["food"][item["retailer_id"]] = product_info 
                key = "restaurant:"   
                desc=item.get("description", "")
                index = desc.lower().find(key)
                if index != -1:
                     restaurant = desc[index + len(key):].strip().title()
                     if restaurant not in restaurants:
                       restaurants[restaurant]=[]
                     
                     restaurants[restaurant].append(rid) 
                     print(restaurant,rid)  # Output: AFC chicken
                else:
                     print("Restaurant not found.",rid)
                pass
        # categorized['food']=restaurants

        with open("restaurants.json", "w", encoding="utf-8") as f:
            json.dump(restaurants, f, ensure_ascii=False, indent=2)
        with open("result.json", "w", encoding="utf-8") as f:
            json.dump(categorized, f, ensure_ascii=False, indent=2)
        
        
        return categorized

    except Exception as e:
        print(e)
        return {"status": "error", "message": str(e)}


WHATSAPP_API_URL = "https://graph.facebook.com/v22.0/579242655280457/messages"
WHATSAPP_TOKEN = os.getenv("ACCESS_TOKEN")
def load_products_by_category(category: str):
    try:
        with open("result.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            
        return data.get(category, {})
    except Exception as e:
        print("hhh",e)
        return {}
def load_restaurants(restaurant=None):
    try:
        with open("restaurants.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            
        return data.get(restaurant, []) if restaurant else data
    except Exception as e:
        print("hhh",e)
        return {}
def send_whatsapp_product_list(category: str, to_number: str,restaurant=None):
    
    if isinstance(category, list) and not category[0] in ["vegetables","fruits","oth","meat","fish","bakeries"]:
        product_items = [{"product_retailer_id": rid} for rid in category]
        senditems(to_number,product_items)

    elif restaurant:
        product_items=load_restaurants(restaurant)
        product_items = [{"product_retailer_id": rid} for rid in product_items]
        senditems(to_number,product_items)
        
    else:
        # Otherwise, load from file
     print("hello")
     if isinstance(category, str):
      category = [category] 
     for i in category:
        print(1111)
        product_dict = load_products_by_category(i)
        print(product_dict)
        print(222)
        if not product_dict:
            return {"status": "error", "message": "Category not found or empty"}
        product_items = [{"product_retailer_id": rid} for rid in product_dict.keys()]
        # print(product_items)
        senditems(to_number,product_items)
        
    return

def senditems(to_number, product_items):
 

 print(len(product_items))

 if len(product_items)>30: 
       product_items= split_list(product_items)
 else:
     product_items=[product_items]

 for i in product_items:
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "interactive",
        "interactive": {
            "type": "product_list",
            "header": {
                "type": "text",
                "text": "🛒 Anghadi Specials"
            },
            "body": {
                "text": "Check out our  products! \n ഉത്പന്നങ്ങൾക്കായി  ലിസ്റ്റ്  പരിശോധിക്കുക !"
            },
            "footer": {
                "text": "Tap a product to view more."
            },
            "action": {
                "catalog_id": "1595768864475137",
                "sections": [
                    {
                        "title": "Popular Items",
                        "product_items": i
                    }
                ]
            }
        }
    }

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    print(payload)
    try:
        response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
        response.raise_for_status()
       
    except requests.exceptions.RequestException as e:
        print(e)
        return {"status": "error", "message": str(e)}
 return {"status": "success", "response": response.json()}
def split_list(lst, chunk_size=30):
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]