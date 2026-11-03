import csv
import math

def load_csv_to_list_of_dicts(file_path):
    """
    Reads a CSV file and returns a list of dictionaries.
    """
    data = []
    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(dict(row))
    except FileNotFoundError:
        print(f"Error: The file at '{file_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return data

def bearing(lat1, lon1, lat2, lon2):
    """
    Calculates the compass bearing from point 1 to point 2.

    Args:
        lat1, lon1 (float) : Start point (decimal degrees)
        lat2, lon2 (float) : End point (decimal degrees)

    Returns:
        Float : Bearing in degrees, clockwise from North [0, 360).
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_lon = math.radians(lon2 - lon1)

    x = math.sin(d_lon) * math.cos(phi2)
    y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(d_lon)

    return (math.degrees(math.atan2(x, y)) + 360) % 360

def track_headings(latitudes, longitudes, closed_loop=True):
    """
    Calculates the car heading at every track point (direction towards the next point).

    Args:
        latitudes (list[float]) : Latitude of every track point, in driving order
        longitudes (list[float]) : Longitude of every track point, in driving order
        closed_loop (bool) : If True the last point heads back to the first point,
                             otherwise it keeps the previous heading

    Returns:
        List[float] : Heading in degrees clockwise from North, one per point (car_heading).
    """
    n = len(latitudes)
    headings = []

    for i in range(n - 1):
        headings.append(bearing(latitudes[i], longitudes[i], latitudes[i + 1], longitudes[i + 1]))

    if closed_loop:
        headings.append(bearing(latitudes[-1], longitudes[-1], latitudes[0], longitudes[0]))
    else:
        headings.append(headings[-1])

    return headings

def load_track_headings(file_path, closed_loop=True):
    """
    Reads a track coordinates CSV (columns 'latitude', 'longitude') and returns the heading at every point.

    Args:
        file_path (str) : Path to the CSV, e.g. Preprocessing/track_coordinates.csv
        closed_loop (bool) : See track_headings()

    Returns:
        List[float] : Heading in degrees clockwise from North, one per point (car_heading).
    """
    rows = load_csv_to_list_of_dicts(file_path)
    latitudes = [float(row['latitude']) for row in rows]
    longitudes = [float(row['longitude']) for row in rows]

    return track_headings(latitudes, longitudes, closed_loop)
