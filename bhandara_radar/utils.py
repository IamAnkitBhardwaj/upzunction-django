import requests
import re
import math

def extract_coordinates(url):
    """
    Takes a Google Maps URL, follows any redirects, and uses regex 
    to extract the exact Latitude and Longitude.
    """
    try:
        # We use a User-Agent so Google doesn't block us as a bot
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
        
        # When goo.gl redirects, the final URL usually contains the coordinates like @26.8467,80.9462
        final_url = response.url

        # Search for the @lat,lng pattern
        match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', final_url)
        if match:
            lat = float(match.group(1))
            lng = float(match.group(2))
            return lat, lng
            
        return None, None
    except Exception as e:
        print(f"URL Extraction Error: {e}")
        return None, None


def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculates the exact distance (in kilometers) between two GPS points 
    over the spherical curve of the Earth.
    """
    # If any coordinate is missing, we cannot calculate distance
    if not all([lat1, lon1, lat2, lon2]):
        return float('inf')

    # Radius of the Earth in kilometers
    R = 6371.0

    # Convert coordinates to radians for the math equation
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine Formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    
    # Return distance rounded to 2 decimal places (e.g., 1.45 km)
    return round(distance, 2)