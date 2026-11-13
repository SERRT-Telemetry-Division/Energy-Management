import numpy as np
import matplotlib.pyplot as plt
from Aerodynamics.aerodynamics import aerodynamic_drag

# Plot colors (categorical order, never cycled) and recessive ink for axes/text
PLOT_COLORS = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100']
PLOT_INK = '#52514e'
PLOT_GRID = '#e4e3df'

def style_axes(ax, title, xlabel, ylabel):
    """
    Applies the shared plot style: recessive grid/axes, zero line, title and labels.
    """
    ax.set_title(title, loc='left', fontsize=12, color='#0b0b0b')
    ax.set_xlabel(xlabel, color=PLOT_INK)
    ax.set_ylabel(ylabel, color=PLOT_INK)
    ax.tick_params(colors=PLOT_INK)
    ax.grid(True, color=PLOT_GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.axhline(0, color=PLOT_INK, linewidth=0.8)

    for side in ['top', 'right']:
        ax.spines[side].set_visible(False)
    for side in ['left', 'bottom']:
        ax.spines[side].set_color(PLOT_GRID)

def plot_drag_along_track(headings, car_speed, wind_speed, wind_dir, ax=None):
    """
    Plots the aerodynamic drag at every track point for a fixed wind, compared against no wind.

    Args:
        headings (list[float]) : Car heading at every track point (from track.load_track_headings())
        car_speed (float) : Car speed (m/s)
        wind_speed (float) : True wind speed (m/s)
        wind_dir (float) : Direction the wind blows FROM, clockwise from North (deg)
        ax (matplotlib Axes) : Optional axes to draw on, a new figure is made if None

    Returns:
        matplotlib Axes
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(10, 4.5))

    points = range(1, len(headings) + 1)
    drag = [aerodynamic_drag(car_speed, h, wind_speed, wind_dir) for h in headings]
    drag_no_wind = aerodynamic_drag(car_speed, 0, 0, 0)

    ax.plot(points, drag, color=PLOT_COLORS[0], linewidth=2,
            label=f'Wind {wind_speed} m/s from {wind_dir}°')
    ax.axhline(drag_no_wind, color=PLOT_COLORS[1], linewidth=2, linestyle='--', label='No wind')

    style_axes(ax, f'Aerodynamic drag around the track (car at {car_speed} m/s)',
               'Track point', 'Drag (N)')
    ax.legend(frameon=False, labelcolor=PLOT_INK)

    return ax

def plot_drag_vs_wind_direction(car_speed, car_heading, wind_speeds=(0, 5, 10), ax=None):
    """
    Plots the aerodynamic drag as the wind direction sweeps 0-360°, one line per wind speed.

    Args:
        car_speed (float) : Car speed (m/s)
        car_heading (float) : Direction the car travels, clockwise from North (deg)
        wind_speeds (list[float]) : Wind speeds to compare (m/s), at most 4
        ax (matplotlib Axes) : Optional axes to draw on, a new figure is made if None

    Returns:
        matplotlib Axes
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(10, 4.5))

    wind_dirs = np.arange(0, 361, 2)

    for i, wind_speed in enumerate(wind_speeds):
        drag = [aerodynamic_drag(car_speed, car_heading, wind_speed, d) for d in wind_dirs]
        ax.plot(wind_dirs, drag, color=PLOT_COLORS[i], linewidth=2, label=f'{wind_speed} m/s')

    # Mark where the wind is a pure headwind / tailwind for this heading
    ax.axvline(car_heading % 360, color=PLOT_INK, linewidth=0.8, linestyle=':')
    ax.axvline((car_heading + 180) % 360, color=PLOT_INK, linewidth=0.8, linestyle=':')
    ax.text(car_heading % 360, ax.get_ylim()[1], ' headwind', color=PLOT_INK, va='top', fontsize=9)
    ax.text((car_heading + 180) % 360, ax.get_ylim()[1], ' tailwind', color=PLOT_INK, va='top', fontsize=9)

    style_axes(ax, f'Aerodynamic drag vs wind direction (car at {car_speed} m/s heading {car_heading}°)',
               'Wind direction, blowing FROM (deg from North)', 'Drag (N)')
    ax.set_xlim(0, 360)
    ax.set_xticks(range(0, 361, 45))
    ax.legend(title='Wind speed', frameon=False, labelcolor=PLOT_INK)

    return ax
