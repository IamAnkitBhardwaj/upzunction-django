from django.shortcuts import render
from django.http import JsonResponse

from .models import (
    State,
    City,
    TouristSpot
)

from bhandara_radar.utils import (
    calculate_haversine_distance
)

def tourism_feed(request):

    states = State.objects.all().order_by('name')

    spots = TouristSpot.objects.filter(
        is_active=True
    ).select_related(
        'city',
        'city__state'
    ).order_by('-rating')

    context = {
        'states': states,
        'spots': spots
    }

    return render(
        request,
        'tourism/feed.html',
        context
    )

def api_cities(request):

    state_id = request.GET.get('state')

    cities = City.objects.filter(
        state_id=state_id
    ).order_by('name')

    data = []

    for city in cities:

        data.append({
            'id': city.id,
            'name': city.name
        })

    return JsonResponse({
        'cities': data
    })

def api_tourist_spots(request):

    city_id = request.GET.get('city')

    spots = TouristSpot.objects.filter(
        city_id=city_id,
        is_active=True
    )

    results = []

    for spot in spots:

        results.append({

            'id': spot.id,

            'name': spot.name,

            'city': spot.city.name,

            'state': spot.city.state.name,

            'rating': spot.rating,

            'views': spot.views,

            'description': (
                spot.description[:150]
                if spot.description
                else ''
            ),

            'image': (
                spot.image.url
                if spot.image
                else ''
            ),

            'map_url': spot.google_maps_url
        })

    return JsonResponse({
        'spots': results
    })

def api_nearest_tourist_spots(request):

    user_lat = request.GET.get('lat')
    user_lng = request.GET.get('lng')

    if not user_lat or not user_lng:

        return JsonResponse({
            'error': 'GPS missing'
        }, status=400)

    user_lat = float(user_lat)
    user_lng = float(user_lng)

    spots = TouristSpot.objects.filter(
        is_active=True
    )

    results = []

    for spot in spots:

        if (
            spot.latitude is None or
            spot.longitude is None
        ):
            continue

        distance = calculate_haversine_distance(
            user_lat,
            user_lng,
            spot.latitude,
            spot.longitude
        )

        results.append({

            'id': spot.id,

            'name': spot.name,

            'city': spot.city.name,

            'state': spot.city.state.name,

            'distance': distance,

            'rating': spot.rating,

            'views': spot.views,

            'image': (
                spot.image.url
                if spot.image
                else ''
            ),

            'description': (
                spot.description[:150]
                if spot.description
                else ''
            ),

            'map_url': spot.google_maps_url
        })

    results.sort(
        key=lambda x: x['distance']
    )

    return JsonResponse({
        'spots': results
    })
