"""
Runs the aerodynamic drag simulation and shows the plots.

Usage (from the Energy-Management folder):
    venv\\Scripts\\python.exe src\\EnergyManagement\\Simulation.py
    venv\\Scripts\\python.exe src\\EnergyManagement\\Simulation.py --speed 25 --wind-speed 8 --wind-dir 90
    venv\\Scripts\\python.exe src\\EnergyManagement\\Simulation.py --save docs/drag.png
"""
import argparse
import os
import matplotlib.pyplot as plt
from track import load_track_headings
from plots import plot_drag_along_track, plot_drag_vs_wind_direction

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
DEFAULT_COORDS = os.path.join(PROJECT_ROOT, 'Preprocessing', 'track_coordinates.csv')

def parse_args():
    parser = argparse.ArgumentParser(description='Aerodynamic drag simulation around the track.')
    parser.add_argument('--speed', type=float, default=20, help='Car speed (m/s)')
    parser.add_argument('--heading', type=float, default=0, help='Car heading for the wind sweep plot (deg from North)')
    parser.add_argument('--wind-speed', type=float, default=5, help='True wind speed for the track plot (m/s)')
    parser.add_argument('--wind-dir', type=float, default=0, help='Direction the wind blows FROM (deg from North)')
    parser.add_argument('--sweep-speeds', type=float, nargs='+', default=[0, 5, 10],
                        help='Wind speeds compared in the wind sweep plot (m/s), at most 4')
    parser.add_argument('--coords', default=DEFAULT_COORDS, help='Track coordinates CSV')
    parser.add_argument('--save', help='Save the figure to this path instead of only showing it')
    parser.add_argument('--no-show', action='store_true', help='Do not open the plot window')
    return parser.parse_args()

def main():
    args = parse_args()

    headings = load_track_headings(args.coords)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 9))
    plot_drag_along_track(headings, car_speed=args.speed, wind_speed=args.wind_speed, wind_dir=args.wind_dir, ax=ax1)
    plot_drag_vs_wind_direction(car_speed=args.speed, car_heading=args.heading, wind_speeds=args.sweep_speeds, ax=ax2)
    fig.tight_layout()

    if args.save:
        fig.savefig(args.save, dpi=150)
        print(f'Saved figure to {os.path.abspath(args.save)}')
    if not args.no_show:
        plt.show()

if __name__ == "__main__":
    main()
