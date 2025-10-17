import math
# 11.358386753972075, 75.91277067332773
# lat, lon, ref_lat=11.360499024193635, ref_lon=75.90958223007394, radius_km=2):
def is_within_radius(lat, lon, ref_lat=11.358386753972075, ref_lon=75.91277067332773, radius_km=6):
    # Radius of Earth in kilometers
    R = 6371.0

    # Convert degrees to radians
    lat1_rad = math.radians(ref_lat)
    lon1_rad = math.radians(ref_lon)
    lat2_rad = math.radians(lat)
    lon2_rad = math.radians(lon)

    # Difference between points
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad                                                     

    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance_km = R * c

    # Check if distance is within radius
    return distance_km <= radius_km


def calculate_price(lat, lon):
    # Reference point coordinates
    ref_lat = 11.358386753972075
    ref_lon = 75.91277067332773
    
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert latitude and longitude to radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    ref_lat_rad = math.radians(ref_lat)
    ref_lon_rad = math.radians(ref_lon)
    
    # Differences in coordinates
    dlat = ref_lat_rad - lat_rad
    dlon = ref_lon_rad - lon_rad
    
    # Haversine formula
    a = math.sin(dlat/2)**2 + math.cos(lat_rad) * math.cos(ref_lat_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    # Price calculation
    if distance <= 3:
        price = 30
    else:
        price = 30 + (distance - 3) * 8
    
    return round(price, 2)

def check_product_mix(items):
    prefixes = {item['product_retailer_id'][:2] for item in items if 'product_retailer_id' in item}

    has_rf = 'rf' in prefixes
    has_bk = 'bk' in prefixes or 'sn' in prefixes
    has_other = bool(prefixes - {'rf', 'bk'})  # others like sn, veg, gr, etc.

    
    if len(items) > 10:
        if (has_rf or has_bk) and has_other:
            return 10
        else:
            return 5
    elif (has_rf or has_bk) and has_other:
        return 5
    elif has_rf and has_bk:
        return 5
    else:
        return 0



# import re
# from rapidfuzz import fuzz, process

# def remove_emojis_and_specials(text: str) -> str:
#     # Remove emojis and special characters, keep alphanumeric + spaces
#     return re.sub(r'[^a-zA-Z0-9\s]', '', text)

# def fuzzy_best_match(query: str, choices: list[str], score_cutoff: int = 70) -> str | None:
#     # Clean the query
#     clean_query = remove_emojis_and_specials(query).lower()

#     # Build mapping of cleaned -> original
#     cleaned_choices = {remove_emojis_and_specials(c).lower(): c for c in choices}

   
#     # Step 1: try full ratio
#     result = process.extractOne(
#         clean_query,
#         list(cleaned_choices.keys()),
#         scorer=fuzz.ratio,
#         score_cutoff=score_cutoff
#     )

#     # Step 2: fallback to partial ratio if no strong match
#     if result is None:
#         result = process.extractOne(
#             clean_query,
#             list(cleaned_choices.keys()),
#             scorer=fuzz.partial_ratio,
#             score_cutoff=score_cutoff
#         )

#     if result is None:
#         return None

#     match, score, _ = result
#     return cleaned_choices[match]




import re
from rapidfuzz import fuzz, process

# special cases where partial match should be applied
PARTIAL_MATCH_WORDS = {"afc", "dominos", "mcd"}

def remove_emojis_and_specials(text: str) -> str:
    return re.sub(r'[^a-zA-Z0-9\s]', '', text)

def fuzzy_best_match(query: str, choices: list[str], score_cutoff: int = 90) -> str | None:
    clean_query = remove_emojis_and_specials(query).lower().strip()
    cleaned_choices = {remove_emojis_and_specials(c).lower().strip(): c for c in choices}
    print("cleaned_choices:", cleaned_choices)
    # default: full ratio
    scorer = fuzz.ratio  

    # ✅ Only switch to partial if query is exactly in the special words list
    if clean_query in PARTIAL_MATCH_WORDS:
        scorer = fuzz.partial_ratio

    result = process.extractOne(
        clean_query,
        list(cleaned_choices.keys()),
        scorer=scorer,
        score_cutoff=score_cutoff
    )

    if result is None:
        return None

    match, score, _ = result
    print("score:", score)
    return cleaned_choices[match]


