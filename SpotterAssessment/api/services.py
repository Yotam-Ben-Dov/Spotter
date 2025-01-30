import requests
import polyline
from django.conf import settings
from shapely.geometry import LineString, Point
import SpotterAssessment
from .models import FuelStation

geodesic = pyproj.Geod(ellps='WGS84')

def get_route_data(start, end):
    access_token = settings.MAPBOX_ACCESS_TOKEN
    url = f'https://api.mapbox.com/directions/v5/mapbox/driving/{start};{end}'
    params = {
        'geometries': 'geojson',
        'access_token': access_token,
        'steps': 'true',
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None
    return response.json()

def calculate_distance_along_route(route_coords, point):
    route_line = LineString(route_coords)
    nearest_point = route_line.interpolate(route_line.project(point))
    total_distance = 0.0
    for i in range(1, len(route_coords)):
        prev, curr = route_coords[i-1], route_coords[i]
        segment_line = LineString([prev, curr])
        if segment_line.intersects(nearest_point):
            _, _, dist_full = geodesic.inv(prev[0], prev[1], curr[0], curr[1])
            _, _, dist_part = geodesic.inv(prev[0], prev[1], nearest_point.x, nearest_point.y)
            total_distance += dist_part
            break
        else:
            _, _, dist = geodesic.inv(prev[0], prev[1], curr[0], curr[1])
            total_distance += dist
    return total_distance * 0.000621371  # meters to miles

def project_stations(route_coords, stations, max_distance=10):
    route_line = LineString(route_coords)
    projected = []
    for station in stations:
        station_point = Point(station.lon, station.lat)
        if route_line.distance(station_point) * 111 > max_distance:
            continue
        distance_along = calculate_distance_along_route(route_coords, station_point)
        projected.append({'station': station, 'distance': distance_along})
    return sorted(projected, key=lambda x: x['distance'])

def calculate_optimal_route(start, end):
    route_data = get_route_data(start, end)
    if not route_data:
        return {'error': 'Route not found'}
    
    route_coords = [(c[0], c[1]) for c in route_data['routes'][0]['geometry']['coordinates']]
    total_distance_miles = route_data['routes'][0]['distance'] * 0.000621371

    stations = FuelStation.objects.all()
    projected = project_stations(route_coords, stations)

    current_pos = 0.0
    current_fuel = 500.0
    total_cost = 0.0
    stops = []

    while current_pos + current_fuel < total_distance_miles:
        max_reach = current_pos + current_fuel
        candidates = [p for p in projected if current_pos < p['distance'] <= max_reach]
        if not candidates:
            return {'error': 'No stations in range'}
        
        cheapest = min(candidates, key=lambda x: x['station'].price)
        station = cheapest['station']
        distance_to = cheapest['distance'] - current_pos

        remaining_fuel = current_fuel - distance_to
        fuel_needed = (500 - remaining_fuel) / 10
        total_cost += fuel_needed * station.price

        stops.append({
            'name': station.name,
            'location': [station.lat, station.lon],
            'price_per_gallon': station.price,
            'fuel_added': fuel_needed,
            'cost': fuel_needed * station.price
        })

        current_pos = cheapest['distance']
        current_fuel = 500.0

    route_polyline = polyline.encode([(c[1], c[0]) for c in route_coords])
    markers = [f"pin-s+ff0000({s['station'].lon},{s['station'].lat})" for s in projected if s in [cheapest]]
    map_url = f"https://api.mapbox.com/styles/v1/mapbox/streets-v11/static/path-5+f44-0.5({route_polyline})/{','.join(markers)}/auto/600x600?access_token={settings.MAPBOX_ACCESS_TOKEN}"

    return {
        'total_cost': round(total_cost, 2),
        'stops': stops,
        'map_url': map_url
    }