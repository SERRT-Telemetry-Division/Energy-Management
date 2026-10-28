import time
from dataclasses import dataclass
import math
from collections import deque
from scipy.optimize import minimize
import numpy as np
# PHYSICAL VEHICLE VARIABLES
@dataclass
class VehicleConfig:
    mass: float = 453.592                   # Car's Mass (kg)
    solar_array_area: float = 5.797         # Solar array area (m²
    drag_coefficient: float = 0.19          # Drag Coefficient (Cd)
    rolling_resistance: float = 0.005       # Friction Coefficient (Cr)
    frontal_area: float = 1.93              # Frontal car area for aero drag (m²)
    energy_cap: float = 19440000            # Battery energy capacity (Joules)
    n_motor: float = 0.95                   # Motor Efficiency
    n_elec: float = 0.22                    # Battery Efficiency
    p_aux: float = 14.14                    # Perdida de power auxiliar (W)
    alpha_start = 0.4                       # %/100
    orientation = 0                         # deg


def get_speed():
    pass

def get_state_of_charge():
    pass

