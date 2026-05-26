import requests

def get_weather(lat, lon):

    url = "https://api.open-meteo.com/v1/forecast"
    
    # Define the data we want from the API
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,surface_pressure,cloud_cover,precipitation,wind_speed_10m",
        "wind_speed_unit": "ms" # Explicitly request m/s to match your physics equations
    }
    
    try:
        # Send the GET request to Open-Meteo
        response = requests.get(url, params=params)
        response.raise_for_status() # Catches any connection/HTTP errors
        data = response.json()
        
        # Parse the JSON payload
        current = data["current"]
        
        # Extract variables
        temp_c = current["temperature_2m"]
        pressure_hpa = current["surface_pressure"]
        cloud_cover = current["cloud_cover"]
        rain_mm = current["precipitation"]
        wind_speed_ms = current["wind_speed_10m"]
        ghi = current["shortwave_radiation"]
        
        # --- AIR DENSITY CALCULATION ---
        # 1. Convert temperature from Celsius to Kelvin
        temp_k = temp_c + 273.15
        
        # 2. Convert pressure from hectopascals (hPa) to Pascals (Pa)
        pressure_pa = pressure_hpa * 100
        
        # 3. Apply Ideal Gas Law: rho = P / (R * T)
        # R_specific for dry air is 287.05 J/(kg·K)
        R_specific = 287.05
        air_density = pressure_pa / (R_specific * temp_k)
        
        # Output the results
        print("--- Real-Time Environmental Variables ---")
        print(f"Cloud Cover:       {cloud_cover} %")
        print(f"Precipitation:     {rain_mm} mm")
        print(f"Wind Speed (v_w):  {wind_speed_ms} m/s")
        print(f"Temperature:       {temp_c} °C")
        print(f"Surface Pressure:  {pressure_hpa} hPa")
        print(f"Air Density (rho): {air_density:.4f} kg/m³")
        print(f"GHI:               {ghi:.4f} W/m²")
        
        # Return as a dictionary so your main script can use these values
        return {
            "cloud_cover": cloud_cover,
            "v_w": wind_speed_ms,
            "rho": air_density,
            "ghi": ghi,
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Open-Meteo: {e}")
        return None

LATITUDE = 18.2013
LONGITUDE = -67.1452

if __name__ == "__main__":
    constants = get_weather(LATITUDE, LONGITUDE)
    constants["car"] = {
        "mass"      :  453.592,
        "Cd"        :  0.19,
        "Apv"       :  5.797,
        'n_motor'   :  0.95,
        "n_elec"    :   

    }
    