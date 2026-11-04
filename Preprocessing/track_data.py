import xml.etree.ElementTree as ET
import csv
import json
import math
import urllib.request

def get_terrain_elevations(points):
    """
    Queries the free Open-Meteo Elevation API using Python's built-in urllib
    to get the real terrain height (m) for each (latitude, longitude) point.
    """
    elevations = []
    # Process in batches of 100 coordinates per request
    for i in range(0, len(points), 100):
        batch = points[i:i + 100]
        lats = ",".join(f"{p['latitude']:.6f}" for p in batch)
        lons = ",".join(f"{p['longitude']:.6f}" for p in batch)
        
        url = f"https://api.open-meteo.com/v1/elevation?latitude={lats}&longitude={lons}"
        req = urllib.request.urlopen(url)
        data = json.loads(req.read().decode('utf-8'))
        elevations.extend(data["elevation"])
        
    return elevations

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculates horizontal distance in meters between two GPS coordinates."""
    R = 6371000.0  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0)**2
    return 2.0 * R * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

def calculate_heading(lat1, lon1, lat2, lon2):
    """Calculates compass heading (0-360 degrees) from point 1 to point 2."""
    lat1_r, lon1_r = math.radians(lat1), math.radians(lon1)
    lat2_r, lon2_r = math.radians(lat2), math.radians(lon2)
    dlon = lon2_r - lon1_r
    
    x = math.cos(lat2_r) * math.sin(dlon)
    y = math.cos(lat1_r) * math.sin(lat2_r) - math.sin(lat1_r) * math.cos(lat2_r) * math.cos(dlon)
    return (math.degrees(math.atan2(x, y)) + 360.0) % 360.0

def convert_kml(kml_filepath, csv_filepath, json_filepath):
    # Parse the XML tree from the KML file
    tree = ET.parse(kml_filepath)
    root = tree.getroot()
    
    # Define the standard Google Earth KML namespace
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    
    extracted_points = []
    
    # Iterate through all Placemarks (pins, paths, polygons)
    for placemark in root.findall('.//kml:Placemark', ns):
        name_elem = placemark.find('kml:name', ns)
        name = name_elem.text.strip() if name_elem is not None and name_elem.text else "Track_Segment"
        
        # Find all coordinate blocks inside the placemark
        for coord_elem in placemark.findall('.//kml:coordinates', ns):
            if not coord_elem.text:
                continue
            
            # Coordinates in KML are space-separated tuples: lon,lat,alt
            raw_coords = coord_elem.text.strip().split()
            for idx, coord in enumerate(raw_coords):
                parts = coord.split(',')
                if len(parts) >= 2:
                    lon = float(parts[0])
                    lat = float(parts[1])
                    alt = float(parts[2]) if len(parts) > 2 else 0.0
                    
                    extracted_points.append({
                        "point_index": idx + 1,
                        "name": name,
                        "latitude": lat,
                        "longitude": lon,
                        "elevation_m": alt
                    })

    # --- ADDITIONAL CODE 1: Fill missing elevations if KML exported 0.0 ---
    if extracted_points and all(p["elevation_m"] == 0.0 for p in extracted_points):
        print("KML has 0.0 for elevation_m. Fetching real terrain height from Open-Meteo...")
        real_elevations = get_terrain_elevations(extracted_points)
        for i, elev in enumerate(real_elevations):
            extracted_points[i]["elevation_m"] = elev

    # --- ADDITIONAL CODE 2: Approximate distance, incline, and heading per point ---
    accumulated_dist_m = 0.0
    for i in range(len(extracted_points)):
        if i == 0:
            # Starting point has 0 distance/incline from previous point
            extracted_points[i]["distance_m"] = 0.0
            extracted_points[i]["accumulated_m"] = 0.0
            extracted_points[i]["delta_elev_m"] = 0.0
            extracted_points[i]["grade_decimal"] = 0.0
            extracted_points[i]["grade_percent"] = 0.0
            extracted_points[i]["incline_rad"] = 0.0
            extracted_points[i]["heading_deg"] = 0.0
        else:
            prev = extracted_points[i - 1]
            curr = extracted_points[i]
            
            dist_m = haversine_distance(
                prev["latitude"], prev["longitude"],
                curr["latitude"], curr["longitude"]
            )
            accumulated_dist_m += dist_m
            delta_elev = curr["elevation_m"] - prev["elevation_m"]
            
            if dist_m > 0:
                grade_dec = delta_elev / dist_m                  # Rise / Run 
                grade_pct = grade_dec * 100.0                    # Percentage 
                theta_rad = math.atan2(delta_elev, dist_m)       # Angle in radians for math.sin/cos
                heading = calculate_heading(
                    prev["latitude"], prev["longitude"],
                    curr["latitude"], curr["longitude"]
                )
            else:
                grade_dec, grade_pct, theta_rad, heading = 0.0, 0.0, 0.0, 0.0
                
            extracted_points[i]["distance_m"] = round(dist_m, 2)
            extracted_points[i]["accumulated_m"] = round(accumulated_dist_m, 2)
            extracted_points[i]["delta_elev_m"] = round(delta_elev, 2)
            extracted_points[i]["grade_decimal"] = round(grade_dec, 4)
            extracted_points[i]["grade_percent"] = round(grade_pct, 2)
            extracted_points[i]["incline_rad"] = round(theta_rad, 6)
            extracted_points[i]["heading_deg"] = round(heading, 2)

    # Export to CSV
    if extracted_points:
        with open(csv_filepath, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=extracted_points[0].keys())
            writer.writeheader()
            writer.writerows(extracted_points)
            
    # Export to JSON
    with open(json_filepath, mode='w', encoding='utf-8') as json_file:
        json.dump(extracted_points, json_file, indent=4)

    print(f"Successfully exported {len(extracted_points)} GPS points with terrain elevation and incline to {csv_filepath} and {json_filepath}.")

# Example usage:
convert_kml("ozark.kml", "ozark_track_with_incline.csv", "ozark_track_with_incline.json")