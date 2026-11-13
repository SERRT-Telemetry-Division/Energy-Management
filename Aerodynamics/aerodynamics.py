import math
import numpy as np
from EnergyManagement import VehicleConfig

def wind_vectors(car_speed, car_heading, wind_speed, wind_dir):
    """
    Builds the car, true wind and apparent wind vectors (x = East, y = North).

    Args:
        car_speed (float) : Car speed ||Vv|| (m/s)
        car_heading (float) : Direction the car travels, clockwise from North (deg)
        wind_speed (float) : True wind speed ||Vw|| (m/s)
        wind_dir (float) : Direction the wind blows FROM, clockwise from North (deg, meteorological convention)

    Returns:
        Tuple : (v_v, v_w, v_app) as NumPy arrays.
    """
    theta_c = math.radians(car_heading)
    theta_w = math.radians(wind_dir)

    # Car velocity vector Vv
    v_v = np.array([car_speed * math.sin(theta_c), car_speed * math.cos(theta_c)])

    # True wind vector Vw (negative because wind_dir is where the wind comes FROM)
    v_w = np.array([-wind_speed * math.sin(theta_w), -wind_speed * math.cos(theta_w)])

    # Apparent wind seen by the car: Vw - Vv
    v_app = v_w - v_v

    return v_v, v_w, v_app

def yaw_angle(car_speed, car_heading, wind_speed, wind_dir):
    """
    Calculates the yaw angle between the apparent wind and the car's heading using the law of cosines (Eq. 5):

        Y = cos^-1( (||Vw||^2 - ||Vw - Vv||^2 - ||Vv||^2) / (-2 ||Vw - Vv|| ||Vv||) )

    Args:
        car_speed (float) : Car speed ||Vv|| (m/s)
        car_heading (float) : Direction the car travels, clockwise from North (deg)
        wind_speed (float) : True wind speed ||Vw|| (m/s)
        wind_dir (float) : Direction the wind blows FROM, clockwise from North (deg, meteorological convention)

    Returns:
        Float : Yaw angle in degrees (0 = apparent wind straight on the nose, 180 = apparent wind from behind).
    """
    v_v, v_w, v_app = wind_vectors(car_speed, car_heading, wind_speed, wind_dir)

    norm_w = np.linalg.norm(v_w)
    norm_v = np.linalg.norm(v_v)
    norm_app = np.linalg.norm(v_app)

    # Undefined when the car is stopped or the apparent wind is zero
    if norm_v == 0 or norm_app == 0:
        return 0.0

    cos_yaw = (norm_w**2 - norm_app**2 - norm_v**2) / (-2 * norm_app * norm_v)

    # Clip to [-1, 1] to avoid NaN from floating point error
    cos_yaw = np.clip(cos_yaw, -1.0, 1.0)

    return math.degrees(math.acos(cos_yaw))

def aerodynamic_drag(car_speed, car_heading, wind_speed, wind_dir,
                     air_density=1.225,
                     drag_coefficient=VehicleConfig.drag_coefficient,
                     frontal_area=VehicleConfig.frontal_area):
    """
    Calculates the aerodynamic drag along the car's roll axis (Eq. 4):

        Drag = 1/2 * Cd * rho * Ap * ||Vw - Vv||^2 * cos(Y)

    Cd and Ap are treated as constants (not functions of the yaw angle Y).

    Args:
        car_speed (float) : Car speed ||Vv|| (m/s)
        car_heading (float) : Direction the car travels, clockwise from North (deg)
        wind_speed (float) : True wind speed ||Vw|| (m/s)
        wind_dir (float) : Direction the wind blows FROM, clockwise from North (deg)
        air_density (float) : rho (kg/m³)
        drag_coefficient (float) : Cd, constant
        frontal_area (float) : Ap (m²), constant

    Returns:
        Float : Drag force in Newtons (negative means the apparent wind pushes the car forward).
    """
    _, _, v_app = wind_vectors(car_speed, car_heading, wind_speed, wind_dir)
    y = math.radians(yaw_angle(car_speed, car_heading, wind_speed, wind_dir))

    return 0.5 * drag_coefficient * air_density * frontal_area * np.linalg.norm(v_app)**2 * math.cos(y)
