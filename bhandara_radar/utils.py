import requests
import re
import math

def extract_coordinates(url):
    # 1. We create a fake "disguise" so Google thinks Render is a real computer
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    try:
        # 2. We pass the disguise in the request
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        
        # 3. Now Google will let the link expand, and we search for the coordinates
        final_url = response.url
        
        # Your existing regex logic to find @26.xxx,80.xxx goes here...
        match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', final_url)
        if match:
            return float(match.group(1)), float(match.group(2))
            
    except Exception as e:
        print(f"Extraction failed: {e}")
        
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