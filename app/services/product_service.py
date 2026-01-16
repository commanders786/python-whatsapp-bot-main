import json
import logging
import os
import requests

import aiohttp
import asyncio




FACEBOOK_API_URL = "https://graph.facebook.com/v22.0/1595768864475137/products"
ACCESS_TOKEN ="EAAQKF56ZAbJQBO3eHvyzD8AERlnLM7hAvtAIZCcSYubLA7JqPq7iv2NGlzlgDfX1DnJ9CJl9ZANyHdiHYNztdvAjf2C4XKWXFMBCjqTagNJDV4VYV59VhzLQ76kZBjrVP3XDsa2UeqBmT9lr01zgImVXPcmeDsyf6KXOaDk61yFzMKS5BkFZBhDX4tsMfuJ4ZA5QZDZD"


# def  fetch_and_categorize_products():
#     restaurants={}
#     logging.info("Loading and categorizing...")
#     print("Loading products..")
#     try:
#         response = requests.get(
#             FACEBOOK_API_URL,
#             params={
#                 "fields": "id,name,retailer_id,description,price,brand,pattern,availability,sale_price",
#                 "access_token": ACCESS_TOKEN,
#                 "limit": 700
#             }
#         )
#         data = response.json()

#         if "data" not in data:
#             raise Exception("Invalid API response format")

#         products = data["data"]

#         categorized = {
#             "vegetables": {},
#             "oth": {},
#             "fruits": {},
#             "meat":{},
#             "fish":{},
#             "bakeries":{},
#               "food":{},
#               "general":{},
#                "snacks":{},
#                "nuts":{}

#         }

        

#         for item in products:
#             rid = item.get("retailer_id", "").lower()
#             product_info = {
#                 "id": item.get("id"),
#                 "name": item.get("name"),
#                 "description": item.get("description"),
#                 "price": item.get("price"),
#                 "pattern": item.get("pattern") or item.get("brand"),
#                 "unit":item.get("size"),
#                 "retailer_id": item.get("retailer_id"),
#                 "availability": item.get("availability"),
#                 "sale_price":item.get("sale_price"),
#             }

#             if rid.startswith("veg"):
#                 categorized["vegetables"][item["retailer_id"]] = product_info
#             elif rid.startswith("gr"):
#                 categorized["oth"][item["retailer_id"]] = product_info
#             elif rid.startswith("fr"):
#                 categorized["fruits"][item["retailer_id"]] = product_info
#             elif rid.startswith("sn"):
#                 categorized["snacks"][item["retailer_id"]] = product_info
#             elif rid.startswith("bk"):
#                 categorized["bakeries"][item["retailer_id"]] = product_info
#             elif rid.startswith("ch") or rid.startswith("kd") or rid.startswith("wp") or rid.startswith("sk"):
#                 categorized["meat"][item["retailer_id"]] = product_info
#             elif rid.startswith("fs"):
#                 categorized["fish"][item["retailer_id"]] = product_info
#             elif rid.startswith("gn"):
#                 categorized["general"][item["retailer_id"]] = product_info
#             elif rid.startswith("nuts"):
#                 categorized["nuts"][item["retailer_id"]] = product_info
#             elif rid.startswith("rf"):
#                 categorized["food"][item["retailer_id"]] = product_info 
#                 key = "restaurant:"   
#                 desc=item.get("description", "")
#                 index = desc.lower().find(key)
#                 if index != -1:
#                      restaurant = desc[index + len(key):].strip().title()
#                      if restaurant not in restaurants:
#                        restaurants[restaurant]=[]
                     
#                      restaurants[restaurant].append(rid) 
#                     #  print(restaurant,rid)  # Output: AFC chicken
#                 else:
#                      print("Restaurant not found.",rid)
#                 pass
#         # categorized['food']=restaurants

#         with open("restaurants.json", "w", encoding="utf-8") as f:
#             json.dump(restaurants, f, ensure_ascii=False, indent=2)
#         with open("result.json", "w", encoding="utf-8") as f:
#             json.dump(categorized, f, ensure_ascii=False, indent=2)
        
        
#         return categorized

#     except Exception as e:
#         print(e)
#         return {"status": "error", "message": str(e)}

def fetch_and_categorize_products():
    restaurants = {}
    logging.info("Loading and categorizing...")
    print("Loading products..")

    categorized = {
        "vegetables": {},
        "oth": {},
        "fruits": {},
        "meat": {},
        "fish": {},
        "bakeries": {},
        "food": {},
        "general": {},
        "snacks": {},
        "nuts": {},
        "childcare":{}
    }

    try:
        url = FACEBOOK_API_URL
        params = {
            "fields": "id,name,retailer_id,description,price,brand,pattern,availability,sale_price",
            "access_token": ACCESS_TOKEN,
            "limit": 300
        }

        while url:  # keep looping until paging runs out
            response = requests.get(url, params=params)
            data = response.json()

            if "data" not in data:
                raise Exception("Invalid API response format")

            products = data["data"]

            for item in products:
                rid = item.get("retailer_id", "").lower()
                product_info = {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "description": item.get("description"),
                    "price": item.get("price"),
                    "pattern": item.get("pattern") or item.get("brand"),
                    "unit": item.get("size"),
                    "retailer_id": item.get("retailer_id"),
                    "availability": item.get("availability"),
                    "sale_price": item.get("sale_price"),
                }
                desc = item.get("description", "")
                 # 🧩 Add fb_product_category while categorizing
                if rid.startswith("veg"):
                    product_info["fb_product_category"] = "vegetables"
                    categorized["vegetables"][item["retailer_id"]] = product_info
                elif rid.startswith("gr"):
                    product_info["fb_product_category"] = "oth"
                    categorized["oth"][item["retailer_id"]] = product_info
                elif rid.startswith("fr"):
                    product_info["fb_product_category"] = "fruits"
                    categorized["fruits"][item["retailer_id"]] = product_info
                elif rid.startswith("sn") and not "restaurant:" in desc.lower():
                    product_info["fb_product_category"] = "snacks"
                    categorized["snacks"][item["retailer_id"]] = product_info
                elif rid.startswith("bk") and not "restaurant:" in desc.lower():
                    product_info["fb_product_category"] = "bakeries"
                    categorized["bakeries"][item["retailer_id"]] = product_info
                elif rid.startswith(("ch", "kd", "wp", "sk")):
                    product_info["fb_product_category"] = "meat"
                    categorized["meat"][item["retailer_id"]] = product_info
                elif rid.startswith("fs"):
                    product_info["fb_product_category"] = "fish"
                    categorized["fish"][item["retailer_id"]] = product_info
                elif rid.startswith("gn"):
                    product_info["fb_product_category"] = "general"
                    categorized["general"][item["retailer_id"]] = product_info
                elif rid.startswith("nuts"):
                    product_info["fb_product_category"] = "nuts"
                    categorized["nuts"][item["retailer_id"]] = product_info
                elif rid.startswith("cp"):
                    product_info["fb_product_category"] = "childcare"
                    categorized["childcare"][item["retailer_id"]] = product_info
                elif rid.startswith(("rf","bk","sn")):
                    product_info["fb_product_category"] = "food"
                    categorized["food"][item["retailer_id"]] = product_info
                    key = "restaurant:"
                    desc = item.get("description", "")
                    index = desc.lower().find(key)
                    if index != -1:
                        restaurant = desc[index + len(key):].strip().title()
                        if restaurant not in restaurants:
                            restaurants[restaurant] = []
                        # temporarily store name for sorting
                        restaurants[restaurant].append({
                            "retailer_id": rid,
                            "name": item.get("name", "").strip()
                        })
                    else:
                        print("Restaurant not found.", rid)

            # move to next page if available
            url = data.get("paging", {}).get("next")
            params = None  # after first call, use full URL with "next"

          # --- Sort inside each restaurant alphabetically by name ---
        # --- Sort inside each restaurant alphabetically by name ---
        sorted_restaurants = {}
        for restaurant_name, items in restaurants.items():
            sorted_items = sorted(
                items,
                key=lambda x: x["name"].strip().lower() if x["name"] else ""
            )
            sorted_restaurants[restaurant_name] = [item["retailer_id"] for item in sorted_items]

        # --- Optionally, sort restaurants alphabetically too ---
        sorted_restaurants = dict(sorted(sorted_restaurants.items(), key=lambda x: x[0].lower()))
        with open("restaurants.json", "w", encoding="utf-8") as f:
            json.dump(sorted_restaurants, f, ensure_ascii=False, indent=2)
        with open("result.json", "w", encoding="utf-8") as f:
            json.dump(categorized, f, ensure_ascii=False, indent=2)

        return categorized

    except Exception as e:
        print(e)
        return {"status": "error", "message": str(e)}



WHATSAPP_API_URL = "https://graph.facebook.com/v22.0/579242655280457/messages"
WHATSAPP_TOKEN = "EAAQKF56ZAbJQBO3eHvyzD8AERlnLM7hAvtAIZCcSYubLA7JqPq7iv2NGlzlgDfX1DnJ9CJl9ZANyHdiHYNztdvAjf2C4XKWXFMBCjqTagNJDV4VYV59VhzLQ76kZBjrVP3XDsa2UeqBmT9lr01zgImVXPcmeDsyf6KXOaDk61yFzMKS5BkFZBhDX4tsMfuJ4ZA5QZDZD"


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
        
        return {}
async def send_whatsapp_product_list(category: str, to_number: str, restaurant=None):
    
    if isinstance(category, list) and not category[0] in ["vegetables","fruits","oth","meat","fish","bakeries"]:
        
        # matched = {}
        with open('restaurants.json', 'r', encoding="utf-8") as file:
           restaurants = json.load(file)
        for restaurant, ids in restaurants.items():
            common = list(set(ids) & set(category))
            if common:
                product_items = [{"product_retailer_id": rid} for rid in common]
                await senditems(to_number,product_items,restaurant)
                # Remove matched IDs from category
                category = list(set(category) - set(common))
        if category:
            product_items = [{"product_retailer_id": rid} for rid in category]
            print(8888888)
            await senditems(to_number,product_items)

    elif restaurant:
        product_items=load_restaurants(restaurant)
        product_items = [{"product_retailer_id": rid} for rid in product_items]
        print(7777777)
        await senditems(to_number,product_items)
        
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
        await senditems(to_number,product_items)
        
    return

# def senditems(to_number, product_items,restaurant=None):
#  flag=0
 

#  print(len(product_items))
#  if len(product_items)>60: 
#      flag=1
#      product_items=product_items[0:59]
#  if len(product_items)>30: 
#        product_items= split_list(product_items)
#  else:
#      product_items=[product_items]

#  for i in product_items:
#     payload = {
#         "messaging_product": "whatsapp",
#         "to": to_number,
#         "type": "interactive",
#         "interactive": {
#             "type": "product_list",
#             "header": {
#                 "type": "text",
#                 "text": "🛒 Anghadi Specials"
#             },
#             "body": {
#                 "text": restaurant if restaurant else "Check out our  products! \n ഉത്പന്നങ്ങൾക്കായി  ലിസ്റ്റ്  പരിശോധിക്കുക !"
#             },
#             "footer": {
#                 "text": "Tap a product to view more."
#             },
#             "action": {
#                 "catalog_id": "1595768864475137",
#                 "sections": [
#                     {
#                         "title": "Popular Items",
#                         "product_items": i
#                     }
#                 ]
#             }
#         }
#     }

#     headers = {
#         "Authorization": f"Bearer {WHATSAPP_TOKEN}",
#         "Content-Type": "application/json"
#     }
#     print(WHATSAPP_TOKEN)
#     print("heey",payload)
#     try:
#         response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
#         response.raise_for_status()
       
#     except requests.exceptions.RequestException as e:
#         print(e)
#         return {"status": "error", "message": str(e)}
    
   
#  return {"status": "success", "response": response.json()}



async def senditems(to_number, product_items, restaurant=None):
    flag = 0
    print(len(product_items))

    if len(product_items) > 60: 
        flag = 1
        product_items = product_items[0:59]

    if len(product_items) > 30:
        product_items = split_list(product_items)
    else:
        product_items = [product_items]

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in product_items:
            payload = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "interactive",
                "interactive": {
                    "type": "product_list",
                    "header": {"type": "text", "text": "🛒 Anghadi Specials"},
                    "body": {
                        "text": restaurant if restaurant else "Check out our products! \nഉത്പന്നങ്ങൾക്കായി ലിസ്റ്റ് പരിശോധിക്കുക !"
                    },
                    "footer": {"text": "Tap a product to view more."},
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

            print("heey", payload)
            # Send all requests concurrently
            tasks.append(session.post(WHATSAPP_API_URL, headers=headers, json=payload))

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        results = []
        for r in responses:
            if isinstance(r, Exception):
                print(f"Error: {r}")
                results.append({"error": str(r)})
            else:
                try:
                    resp_json = await r.json()
                    results.append(resp_json)
                except Exception as e:
                    results.append({"error": str(e)})

    return {"status": "success", "responses": results}













def split_list(lst, chunk_size=30):
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

# fetch_and_categorize_products()