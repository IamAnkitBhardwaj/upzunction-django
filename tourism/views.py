from django.shortcuts import render
from django.http import JsonResponse

from tourism.forms import TouristSpotForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import login_required

from .forms import TouristSpotForm
from .models import TouristSpot

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
        is_active=True,
        is_approved=True
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

@login_required
def add_tourist_spot(request):

    if request.method == 'POST':

        form = TouristSpotForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            spot = form.save(commit=False)

            spot.user = request.user

            spot.is_approved = False

            spot.save()

            return redirect('dashboard')

    else:

        form = TouristSpotForm()

    return render(
        request,
        'tourism/add_spot.html',
        {
            'form': form
        }
    )

@login_required
def edit_tourist_spot(
    request,
    spot_id
):

    spot = get_object_or_404(
        TouristSpot,
        id=spot_id,
        user=request.user
    )

    if request.method == 'POST':

        form = TouristSpotForm(
            request.POST,
            request.FILES,
            instance=spot
        )

        if form.is_valid():

            form.save()

            return redirect(
                'dashboard'
            )

    else:

        form = TouristSpotForm(
            instance=spot
        )

    return render(
        request,
        'tourism/edit_spot.html',
        {
            'form': form
        }
    )

@login_required
def delete_tourist_spot(
    request,
    spot_id
):

    spot = get_object_or_404(
        TouristSpot,
        id=spot_id,
        user=request.user
    )

    if request.method == 'POST':

        spot.delete()

        return redirect(
            'dashboard'
        )

    return render(
        request,
        'tourism/delete_spot.html',
        {
            'spot': spot
        }
    )

def tourist_spot_detail(
    request,
    spot_id
):

    spot = get_object_or_404(
        TouristSpot,
        id=spot_id,
        is_active=True
    )

    spot.views += 1
    spot.save()

    return render(
        request,
        'tourism/detail.html',
        {
            'spot': spot
        }
    )

def tourist_spot_detail(
    request,
    spot_id
):

    spot = get_object_or_404(
        TouristSpot,
        id=spot_id,
        is_active=True
    )

    # View Counter
    spot.views += 1

    spot.save(
        update_fields=['views']
    )

    # Related Places
    related_spots = TouristSpot.objects.filter(
        city=spot.city,
        is_active=True
    ).exclude(
        id=spot.id
    )[:6]

    context = {

        'spot': spot,

        'related_spots': related_spots

    }

    return render(
        request,
        'tourism/detail.html',
        context
    )