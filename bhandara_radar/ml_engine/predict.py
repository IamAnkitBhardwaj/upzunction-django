import joblib
import os
from datetime import datetime
from django.conf import settings
from bhandara_radar.utils import calculate_haversine_distance
# Load the ML model once when the server starts
MODEL_PATH = os.path.join(settings.BASE_DIR, 'bhandara_radar', 'ml_engine', 'crowd_model.joblib')

try:
    crowd_model = joblib.load(MODEL_PATH)
except Exception as e:
    crowd_model = None
    print(f"Warning: ML model not found. {e}")

def get_live_crowd_prediction(area_name):
    """
    Feeds the current time, day, and area into the Random Forest model.
    Returns a tuple: (RAW_STATUS, DISPLAY_TEXT)
    """
    if not crowd_model:
        return 'LOW', 'Moving Fast' # Safety fallback
        
    now = datetime.now()
    hour = now.hour
    day_of_week = now.weekday() # 0 = Monday, 6 = Sunday
    
    # Assign an 'area density score' (1-10). 
    # Since we don't have a live density API, we simulate it based on known busy areas.
    area_score = 5 # Default average density
    if area_name:
        name_lower = area_name.lower()
        if 'alambagh' in name_lower or 'hazratganj' in name_lower or 'charbagh' in name_lower:
            area_score = 9 # High density commercial zones
        elif 'gomti nagar' in name_lower or 'indira nagar' in name_lower:
            area_score = 7

    # 🚀 The AI Prediction!
    # We pass the exact format we trained on: [hour, day_of_week, area_score]
    prediction = crowd_model.predict([[hour, day_of_week, area_score]])[0]
    
    if prediction == 2:
        return 'HIGH', 'Heavy Rush'
    elif prediction == 1:
        return 'MODERATE', 'Moderate Rush'
    else:
        return 'LOW', 'Moving Fast'
    
def get_smart_alternatives(target_bhandara_id, user_lat, user_lng, all_bhandaras):
    """
    Finds the 3 closest alternative Bhandaras that are NOT highly crowded.
    """
    alternatives = []
    
    for b in all_bhandaras:
        # Skip the one we are already looking at
        if b.id == target_bhandara_id:
            continue
            
        # 1. Get the AI prediction for this alternative
        raw_status, display = get_live_crowd_prediction(b.area_name)
        
        # 2. If it is NOT a heavy rush, calculate how far it is from the user
        if raw_status != 'HIGH':
            dist = calculate_haversine_distance(user_lat, user_lng, b.latitude, b.longitude)
            if dist is not None:
                alternatives.append({
                    'id': b.id,
                    'title': b.business_name if b.is_verified_owner else f"📍 {b.area_name}",
                    'distance': dist,
                    'crowd_status': display
                })
    
    # 3. Sort by distance and return the top 3 (K=3 Nearest Neighbors logic)
    alternatives.sort(key=lambda x: x['distance'])
    return alternatives[:3]