# Energy-Management
Energy management system for SERRT.

# Purpose of this branch
Please use this branch when testing out research questions or different ways to implement different algorithms for different features. Create branches from this research branch, develop, and test out solutions before implementing in the main branch.


# Open-Meteo API setup
Run the following commands in the terminal:

- python -m venv venv
- venv\Scripts\activate
- pip install -r requirements.txt
- curl "https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"

The last command is optional for testing Open-Meteo functionality.


