from dataclasses import dataclass
import math
from collections import deque
from scipy.optimize import minimize
import numpy as np

# PHYSICAL VEHICLE VARIABLES
@dataclass
class VehicleConfig:
    mass: float = 268.0                     # kg
    solar_array_area: float = 4.0           # m²
    drag_coefficient: float = 0.16          # Cd
    rolling_resistance: float = 0.0085      # Cr
    frontal_area: float = 1.03              # A (m²)
    energy_cap: float = 17_800_000.0        # Joules
    n_motor: float = 0.96                   # Efficiency
    n_elec: float = 0.20                    # Efficiency
    p_aux: float = 13.0                     # W

# INITIAL ENVIRONMENT READINGS
@dataclass
class EnvironmentState:
    air_density: float               # kg/m³
    ghi: float                       # W/m²
    # You can add initial wind speed, temp, etc. here

class EnergyManager:
    def __init__(self, vehicle_config: VehicleConfig, initial_env: EnvironmentState):
        # Save the config objects
        self.car = vehicle_config
        self.env = initial_env
        
        # Initialize the dynamic real-time data stacks
        self.speed_stack = deque()         
        self.acc_energy_stack = deque()    
        self.p_battery_stack = deque()     
        self.t_k_stack = deque()
        
    #-----------MECHANICAL FORCES-----------
    # Notice how we only pass dynamic variables now; constants are pulled from self.car
    def aerodynamic_drag(self, v, vw):
        return 0.5 * self.env.air_density * self.car.frontal_area * self.car.drag_coefficient * ((v + vw)**2)
    
    def rolling_resistance(self, theta, g=9.81):
        return self.car.rolling_resistance * self.car.mass * g * math.cos(theta)
    
    def grav_force(self, theta, g=9.81):
        return self.car.mass * g * math.sin(theta)
    
    def power_loss(self, vk, F1, F2, F3):
        return (vk / self.car.n_motor) * (F1 + F2 + F3) + self.car.p_aux
    
    #-----------SOLAR AND BATTERY POWER-----------
    def sun_generated_power(self):
        return self.env.ghi * self.car.n_elec * self.car.solar_array_area
    
    def net_battery_energy_flow(self, vk, v, vw, theta):
        # Calculate forces based on current dynamic inputs
        F1 = self.aerodynamic_drag(v, vw)
        F2 = self.rolling_resistance(theta)
        F3 = self.grav_force(theta)
        
        # Calculate power loss and subtract it from generated power
        current_p_loss = self.power_loss(vk, F1, F2, F3)
        return self.sun_generated_power() - current_p_loss
    
    #-----------ACCELERATION ENERGY-----------        
    def acc_energy(self):
        # Safety check: ensure we have at least 2 speed readings
        if len(self.speed_stack) < 2:
            return 0.0
            
        # Get current and previous speed to calculate delta speed
        v_curr = self.speed_stack.pop()
        v_prev = self.speed_stack.pop()

        # Restore History
        self.speed_stack.append(v_prev)
        self.speed_stack.append(v_curr)
         
        # Calculate Energy (Corrected square physics and variable access)
        result = 0.5 * self.car.mass * ((v_curr**2) - (v_prev**2))
        return result
    
    #-----------STATE OF CHARGE-----------
    def state_of_charge(self, alpha_start):
        # Convert deques to numpy arrays for element-wise math
        p_batt_arr = np.array(self.p_battery_stack)
        t_k_arr = np.array(self.t_k_stack)
        
        # Correct element-wise array multiplication, then sum
        steady_energy_sum = np.sum(p_batt_arr * t_k_arr)
        
        # Sum the acceleration energy stack
        accel_energy_sum = np.sum(self.acc_energy_stack)

        # Calculate final percentage
        current_soc = alpha_start + ((steady_energy_sum + accel_energy_sum) / self.car.energy_cap) * 100.0
    
        return current_soc
    
    #-----------STOCHASTIC EXPECTED VALUES-----------
    def expected_sun_power(self, ghi_pmf):
        """
        Args:
            ghi_pmf: A list of tuples containing (probability, predicted_ghi)
                     Example: [(0.2, 200), (0.5, 500), (0.3, 800)]
        """
        # Calculate the expected GHI based on the Probability Mass Function (PMF)
        expected_ghi = sum(probability * ghi for probability, ghi in ghi_pmf)
        
        # Calculate expected solar power using the expected GHI
        return expected_ghi * self.car.n_elec * self.car.solar_array_area
        
    def expected_net_battery_power(self, prev_e_batt, current_e_sun, p_loss):
        """
        Iteratively calculates the expected battery power.
        """
        return prev_e_batt + (current_e_sun - p_loss)
    
    #-----------SPEED OPTIMIZATION (SQP)-----------
    def optimize_route_speeds(self, route_distances, route_inclines, expected_ghi_array, alpha_start, target_alpha_end, allowed_driving_time):
        """
        Calculates the optimal speed vector for a given route using SQP.
        """
        num_intervals = len(route_distances)
        
        # 1. Initial Guess: Assume we drive at a safe middle speed (20 m/s) for the whole route
        initial_speeds = np.full(num_intervals, 20.0) 

        # 2. Objective Function: Maximize final Expected SoC (SciPy only minimizes, so we return negative SoC)
        def objective(speeds):
            # NOTE: In a real implementation, you would loop through the speeds, 
            # calculate expected P_loss, P_sun, and tally the expected SoC here.
            # For brevity in the optimizer setup, we assume a placeholder calculation:
            final_soc = self.state_of_charge(alpha_start) # (Replace with iterative expected SoC calculation)
            return -final_soc 

        # 3. Constraints Setup
        constraints = []
        
        # Constraint Gamma (Time Limit): Total driving time must be close to Allowed Driving Time
        def time_constraint(speeds):
            total_time = np.sum(route_distances / speeds)
            # Must fall within a 300 second window
            return 300.0 - abs(total_time - allowed_driving_time)
        constraints.append({'type': 'ineq', 'fun': time_constraint})
        
        # Constraint Beta (Battery Safety): Final SoC must be >= target for next day
        def battery_constraint(speeds):
            final_soc = objective(speeds) * -1 # Make it positive again
            return final_soc - target_alpha_end
        constraints.append({'type': 'ineq', 'fun': battery_constraint})

        # Constraint Sigma (Motor Thermal Limits): P_loss between -5000W and 5000W
        # We define a helper that ensures max/min power for every interval stays in bounds
        def motor_power_upper_limit(speeds):
            # Calculate power loss for all speeds (pseudo-code)
            # max_power = max([self.power_loss(v, ...) for v in speeds])
            return 5000.0 - 0 # Replace 0 with calculated max_power
            
        def motor_power_lower_limit(speeds):
            # min_power = min([self.power_loss(v, ...) for v in speeds])
            return 0 - (-5000.0) # Replace 0 with calculated min_power
            
        constraints.append({'type': 'ineq', 'fun': motor_power_upper_limit})
        constraints.append({'type': 'ineq', 'fun': motor_power_lower_limit})

        # 4. Bounds (Constraint Tau: Speed limits)
        # Speed must be between 11.11 m/s (40 km/h) and 33.33 m/s (120 km/h)
        speed_bounds = [(11.11, 33.33) for _ in range(num_intervals)]

        # 5. Run the SQP Solver
        result = minimize(
            fun=objective, 
            x0=initial_speeds, 
            method='SLSQP', # Sequential Least SQuares Programming (SciPy's SQP)
            bounds=speed_bounds, 
            constraints=constraints,
            options={'disp': True, 'maxiter': 100}
        )
        
        if result.success:
            return result.x # Returns the array of optimal speeds!
        else:
            print("Optimization failed to find a valid speed profile.")
            return initial_speeds
        
# ------------------ FOR INITIALYZATION ------------------
# my_car = VehicleConfig()

# Fetch API data
# current_rho = 1.225 # Calculated from your weather API
# current_ghi = 800.0 # Fetched from your weather API

# startup_env = EnvironmentState(air_density=current_rho, ghi=current_ghi)

# Initialize EnergyManagement class
# em = EnergyManager(vehicle_config=my_car, initial_env=startup_env)