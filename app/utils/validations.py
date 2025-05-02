import math

def is_within_radius(lat, lon, ref_lat=11.360499024193635, ref_lon=75.90958223007394, radius_km=2):
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
