
import json

import requests

from app.services.product_service import load_restaurants
from app.utils.validations import calculate_price, check_product_mix

def load_all_products():
    with open("result.json", "r", encoding="utf-8") as f:
        return json.load(f)

def build_product_name_map(all_products):
    name_map = {}
    for category in all_products.values():
        for retailer_id, product in category.items():
            name_map[retailer_id] = product.get("name", "Unknown")
    return name_map
import re

def process_order_message(product_items,location=None):
    
   
    # Load product names from result.json
    all_products = load_all_products()
    name_map = build_product_name_map(all_products)
    rows = []
    grand_total = 0

    for idx, item in enumerate(product_items, start=1):
        product_id = item["product_retailer_id"]
        quantity = item["quantity"]
        unit_price = item["item_price"]
        total = quantity * unit_price
        grand_total += total

        # Remove parentheses and contents from name
        full_name_raw = name_map.get(product_id, "Unknown")
        full_name = re.sub(r"\s*\(.*?\)", "", full_name_raw).strip()

        rows.append((str(idx), full_name, str(quantity), f"₹{unit_price}", f"₹{total}"))

    # Calculate max width for each column
    col_widths = [max(len(row[i]) for row in rows + [("No", "Item", "Qty", "Unit", "Total")]) for i in range(5)]

    # Header
    lines = ["🛒 *അങ്ങാടി Ai - PO*\n"]
    header = f"{'No':<{col_widths[0]}}  {'Item':<{col_widths[1]}}  {'Qty':<{col_widths[2]}}  {'Unit':<{col_widths[3]}}  {'Total':<{col_widths[4]}}"
    lines.append(header)
    lines.append("")  # extra line between header and items

    # Rows
    for row in rows:
        line = f"{row[0]:<{col_widths[0]}}  {row[1]:<{col_widths[1]}}  {row[2]:<{col_widths[2]}}  {row[3]:<{col_widths[3]}}  {row[4]:<{col_widths[4]}}"
        lines.append(line)

    if not location:
     lines.append(f"\n🛵 Delivey Charge: ₹ 30")
     grand_total+=30
    else:
     price=calculate_price(location["latitude"],location["longitude"])
    #  handling_charge=calculate_handling_charge(product_items)
     lines.append(f"\n🛵 Delivey Charge: ₹ {str(price)}")
     grand_total+=price


    configs=get_configs()
    print(configs)
    print(type(configs))
    if configs :
      print("11111")
      print(configs.get('isRaincharge'))
    #   if configs.get("isRaincharge") is True:
    #     print(222222)
    #     lines.append(f"\n🌧 Rain Charge: ₹ {str(configs.get('rainCharge'))}")
    #     grand_total+=int(configs.get("rainCharge"))
    handling_charge=check_product_mix(product_items)
    if handling_charge :
        lines.append(f"\n🛍 Multi shop charge: ₹ {str(handling_charge)}")
        grand_total+=handling_charge
     
     
    
    grand_total=round(grand_total,2)
    # Total
    lines.append(f"\n🧾 Grand Total: ₹{grand_total}")
    return ("\n".join(lines),product_items)



import requests
def get_configs():


    url = "https://ashhadmuhammed.pythonanywhere.com/static/anghadiStore.json"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)

        data = response.json()  # Parse JSON response
        print("Data received:")
        print(data)
        return data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
