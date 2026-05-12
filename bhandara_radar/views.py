from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Bhandara
from .forms import BhandaraSubmitForm
from django.http import JsonResponse
from .utils import calculate_haversine_distance
from .ml_engine.predict import get_live_crowd_prediction, get_smart_alternatives
def bhandara_feed(request):
    active_bhandaras = Bhandara.objects.filter(is_approved=True).order_by('-start_time')
    
    # Inject AI prediction into each object for the initial page load
    for b in active_bhandaras:
        raw_status, display_status = get_live_crowd_prediction(b.area_name)
        b.ai_crowd_raw = raw_status
        b.ai_crowd_display = display_status
        
    context = {'bhandaras': active_bhandaras}
    return render(request, 'bhandara_radar/feed.html', context)

def submit_bhandara(request):
    """
    Handles the public submission form.
    """
    if request.method == 'POST':
        form = BhandaraSubmitForm(request.POST)
        if form.is_valid():
            # Save it, but it stays is_approved=False by default!
            new_bhandara = form.save()
            messages.success(request, "Success! Your location has been sent to the Admin for approval. It will be live soon!")
            return redirect('bhandara_radar:feed')
        else:
            messages.error(request, "There was an error with your link. Please try again.")
    else:
        form = BhandaraSubmitForm()

    return render(request, 'bhandara_radar/add_form.html', {'form': form})

def api_nearest_bhandaras(request):
    """
    Receives live GPS coordinates from the frontend, calculates distances, 
    sorts them, and returns JSON.
    """
    user_lat = request.GET.get('lat')
    user_lng = request.GET.get('lng')

    if not user_lat or not user_lng:
        return JsonResponse({'error': 'GPS coordinates missing'}, status=400)

    user_lat = float(user_lat)
    user_lng = float(user_lng)

    # Get all live locations
    active_bhandaras = Bhandara.objects.filter(is_approved=True)
    
    results = []
    for b in active_bhandaras:
        # 1. Calculate distance
        if b.latitude is None or b.longitude is None:
            continue # Skip this location, it has no GPS data!
        distance = calculate_haversine_distance(user_lat, user_lng, b.latitude, b.longitude)
        
        # 2. 🔥 GET LIVE ML PREDICTION 🔥
        raw_status, display_status = get_live_crowd_prediction(b.area_name)
        # 3. 🔥 GET SMART ALTERNATIVES (If crowded) 🔥
        alternatives_data = []
        if raw_status == 'HIGH':
            # We pass the full queryset so the function can scan for neighbors
            alternatives_data = get_smart_alternatives(b.id, user_lat, user_lng, active_bhandaras)
        # 3. Package data
        results.append({
            'id': b.id,
            'title': b.business_name if b.is_verified_owner else f"📍 Active Bhandara - {b.area_name}",
            'area': b.area_name or "Unknown Area",
            'owner': b.organizer_name or "Generous Soul",
            'is_verified': b.is_verified_owner,
            'menu': b.menu_details if b.is_verified_owner else "Menu Unconfirmed",
            'crowd_status': display_status, # Sent by AI
            'crowd_raw': raw_status,        # Sent by AI
            'distance': distance,
            'url': b.google_maps_url,
            'alternatives': alternatives_data # <-- ADD THIS NEW LINE!
        })

    # 3. Sort the list by distance (closest first)
    # We use a lambda function to handle any "None" distances safely
    results.sort(key=lambda x: float('inf') if x['distance'] is None else x['distance'])

    return JsonResponse({'bhandaras': results})