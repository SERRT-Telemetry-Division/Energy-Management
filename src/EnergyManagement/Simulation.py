import csv
import numpy as np
from EnergyManagement import EnergyManager, EnvironmentState, VehicleConfig
import random as rd
import pandas as pd
import os

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

if __name__ == "__main__":
    # Randomize wind speed and direction
    wind_speed = 13.5
    wind_direction = 9

    # Car Velocity Components: Vcx​=Vc​sin(θc​) and Vcy​=Vc​cos(θc​)
    # True Wind Components: Vwx​=−Vw​sin(θw​) and Vwy​=−Vw​cos(θw​)
    # Apparent Wind Components: Vax​=Vwx​−Vcx​ and Vay​=Vwy​−Vcy​
    # Apparent Wind Speed Magnitude: Vapp​=sqrt(Vax2​+Vay2​​)
    # Apparent Wind Angle: θapp​=arctan^2(Vax​,Vay​)
    # Yaw Angle: The absolute difference between your vehicle heading (θc​) and the apparent wind angle (θapp​).

    car = VehicleConfig()
    env = EnvironmentState(
        air_density=1.025,
        ghi=800,
        vw=wind_speed,
        wind_dir=wind_direction
    )

    em = EnergyManager(car, env)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    csv_path = csv_path = os.path.join(project_root, 'docs', 'EM try 2', 'TrackProfile.csv')
    track = load_csv_to_list_of_dicts(csv_path)

    if not os.path.exists(csv_path):
        # This intentionally halts the script and prevents the obscure SciPy crash
        raise FileNotFoundError(
            f"\n[!] Cannot find track profile at '{csv_path}'.\n"
            f"Ensure you are running the script from the correct working directory."
        )

    print("Loading track profile...")
    track_data = pd.read_csv(csv_path)

    # Secondary Guard: Ensure the CSV isn't completely blank
    if track_data.empty:
        raise ValueError("CRITICAL ERROR: TrackProfile.csv was found but is entirely empty.")

    # 1. Randomize global ENVIRONMENTAL wind (Do NOT calculate apparent wind here)
    wind_speed_env = rd.uniform(1.0, 15.0)
    wind_direction_env = rd.randint(0, 360)

    # 2. Extract base arrays directly into NumPy using Pandas (Replaces your DictReader loop)
    route_distances = track_data['Distance (mi)'].fillna(0.0).values
    route_inclines = track_data['Grade (%)'].fillna(0.0).values
    expected_ghi_array = track_data['Irradiance (W/m²)'].fillna(0.0).values
    turns = track_data['Turn (deg)'].fillna(0.0).values

    # 3. Calculate absolute vehicle headings from relative turns
    section_orientations = np.zeros(len(turns))
    current_orientation = 180.0
    for i in range(len(turns)):
        current_orientation += turns[i]
        section_orientations[i] = current_orientation % 360  # Constrain to 0-359 compass degrees

    # 4. Define your global race constraints
    current_soc = em.car.alpha_start     # Starting at 95% battery
    target_soc = 20.0                    # Must cross finish line with at least 20%
    target_time = 3600.0                 # Target driving time in seconds (e.g., 1 hour)

    print("Running optimization (this might take a moment)...")

    # The Function Call
    # This will now safely execute because we guaranteed the arrays are populated.
    optimal_speeds = em.optimize_route_speeds(
        route_distances=route_distances, 
        route_inclines=route_inclines, 
        expected_ghi_array=expected_ghi_array, 
        alpha_start=current_soc, 
        target_alpha_end=target_soc, 
        allowed_driving_time=target_time,
        car_rotation_per_section=section_orientations,
        wind_speed=wind_speed_env
    )

    # # The Function Call (Left exactly as you had it)
    # # This will now safely execute because we guaranteed the arrays are populated.
    # optimal_speeds = em.optimize_route_speeds(
    #     route_distances, 
    #     route_inclines, 
    #     expected_ghi_array, 
    #     car.alpha_start, 
    #     target_alpha_end, 
    #     allowed_driving_time,
    #     car_rotation_per_section,
    #     wind_speed
    # )

    print(f"Wind Speed: ")
    for speed in optimal_speeds:
        print(speed)
    # ... (Proceed with results) ...