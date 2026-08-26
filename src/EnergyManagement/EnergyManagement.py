from dataclasses import dataclass
import math
from collections import deque
from scipy.optimize import minimize
import numpy as np

# PHYSICAL VEHICLE VARIABLES
@dataclass
class VehicleConfig:
    mass: float = 453.592                   # kg
    solar_array_area: float = 5.797         # m²
    drag_coefficient: float = 0.19          # Cd
    rolling_resistance: float = 0.005       # Cr
    frontal_area: float = 1.93              # A (m²)
    energy_cap: float = 19440000            # Joules
    n_motor: float = 0.95                   # Efficiency
    n_elec: float = 0.22                    # Efficiency
    p_aux: float = 14.14                    # W
    alpha_start = 0.4                       # %/100
    orientation = 0                         # deg

# INITIAL ENVIRONMENT READINGS
@dataclass
class EnvironmentState:
    air_density: float                      # kg/m³
    ghi: float                              # W/m²
    vw: float                               # m/s
    wind_dir: float                         # deg
    
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
        self.soc = deque()
        
    #-----------MECHANICAL FORCES-----------
    # Notice how we only pass dynamic variables now; constants are pulled from self.car
    def aerodynamic_drag(self, v_guess, heading_angle, wind_speed, wind_direction_from, rho, frontal_area, cd_base):
        """
        Calculates the actual aerodynamic drag force dynamically based on the 
        optimizer's current speed guess and environmental conditions.
        """
        # Convert API and GPS angles to radians for numpy calculations
        theta_c = np.radians(heading_angle)
        theta_w = np.radians(wind_direction_from)
        
        # Shift the axis: Find wind angle relative to the car's nose
        # Because meteorological wind direction is where the wind is coming FROM
        # If wind is from North (0) and car is heading North (0), relative angle is 0 (direct headwind).
        theta_rel = theta_w - theta_c
        
        # Decompose the environmental wind into headwind and crosswind components
        # This is the "cosine" approach you mentioned, plus the critical sine component.
        v_wind_head = wind_speed * np.cos(theta_rel)
        v_wind_cross = wind_speed * np.sin(theta_rel)
        
        # Calculate apparent wind components using the optimizer's CURRENT speed guess
        # The car's forward motion creates its own relative headwind.
        v_app_head = v_guess + v_wind_head
        v_app_cross = v_wind_cross
        
        # Total apparent wind magnitude squared (required for the drag equation)
        # Notice how a strong crosswind heavily impacts this total magnitude.
        v_app_sq = (v_app_head**2) + (v_app_cross**2)
        
        # Yaw angle calculation
        # To dynamically alter your Cd if the team has wind tunnel data.
        yaw_angle = np.abs(np.degrees(np.arctan2(v_app_cross, v_app_head)))
        
        # Placeholder for yaw-based Cd adjustment
        # cd_dynamic = cd_base * (1 + 0.015 * yaw_angle) 
        
        # Final Drag Force calculation using the true apparent wind
        drag_force = 0.5 * rho * cd_base * frontal_area * v_app_sq
        
        return drag_force
    
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

        self.acc_energy.append(result)
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
        expected_ghi = np.sum(probability * ghi for probability, ghi in ghi_pmf)
        
        # Calculate expected solar power using the expected GHI
        return expected_ghi * self.car.n_elec * self.car.solar_array_area
        
    def expected_net_battery_power(self, prev_e_batt, current_e_sun, p_loss):
        """
        Iteratively calculates the expected battery power.
        """
        return prev_e_batt + (current_e_sun - p_loss)
    

    #-----------SPEED OPTIMIZATION (SQP)-----------
    def optimize_route_speeds(
            self, 
            route_distances, 
            route_inclines, 
            expected_ghi_array, 
            alpha_start, 
            target_alpha_end, 
            allowed_driving_time,
            car_rotation_per_section,
            wind_speed
        ):
        """
        Calculates the optimal speed vector for a given route using SQP.
        """
        num_intervals = len(route_distances)
        
        # Initial Guess: Assume we drive at a safe middle speed (20 m/s) for the whole route
        initial_speeds = np.full(num_intervals, 20.0) 

        # Objective Function: Maximize final Expected SoC (SciPy only minimizes, so we return negative SoC)
        def objective(speeds):
            # Start with your current battery percentage
            predicted_soc = alpha_start
            
            # Loop through every upcoming interval on the route
            for i in range(len(speeds)):
                v_guess = speeds[i]
                dist = route_distances[i]
                theta = route_inclines[i]
                ghi_guess = expected_ghi_array[i]
                
                # Calculate time spent on this segment
                t_k = dist / v_guess
                
                # Calculate the expected physics FOR THIS GUESS
                # (Assuming 0 wind speed for future prediction)
                F1 = self.aerodynamic_drag(
                    v_guess, 
                    car_rotation_per_section[i], 
                    wind_speed,                           # Gathered from weather API
                    car_rotation_per_section[i]+90,       # Gathered from weather API
                    1.225, # air density
                    1.93,  # frontal area
                    0.19   # base drag coefficient
                ) 
                F2 = self.rolling_resistance(theta)
                F3 = self.grav_force(theta)
                
                p_loss = self.power_loss(v_guess, F1, F2, F3)
                p_sun = ghi_guess * self.car.n_elec * self.car.solar_array_area
                p_batt = p_sun - p_loss
                
                # Tally the expected energy flow into the predicted SoC
                segment_energy_joules = p_batt * t_k
                segment_energy_wh = segment_energy_joules / 3600.0  # Convert to Watt-hours
                predicted_soc += (segment_energy_wh / self.car.energy_cap) * 100.0
                
                # Return the negative predicted SoC so SciPy can minimize it

                if predicted_soc > 100.0:
                    predicted_soc = 100.0

            return -predicted_soc 

        # Constraints Setup
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
        def motor_power_upper_limit(speeds):
            p_losses = []
            
            # Loop through the route segments and calculate power loss for each guessed speed
            for i in range(len(speeds)):
                v_guess = speeds[i]
                theta = route_inclines[i]
                
                # Calculate physical forces (Assuming 0 wind speed for future prediction)
                F1 = self.aerodynamic_drag(
                    v_guess, 
                    car_rotation_per_section[i], 
                    wind_speed,                           # Gathered from weather API
                    car_rotation_per_section[i]+90,       # Gathered from weather API
                    1.225, # air density
                    1.93,  # frontal area
                    0.19   # base drag coefficient
                ) 
                F2 = self.rolling_resistance(theta)
                F3 = self.grav_force(theta)
                
                # Calculate the power loss for this specific segment
                segment_p_loss = self.power_loss(v_guess, F1, F2, F3)
                p_losses.append(segment_p_loss)
                
            # Find the highest power draw across the entire route guess
            max_power = max(p_losses)
            
            # The returned value MUST be >= 0 to be valid.
            
            return 5000.0 - max_power

        def motor_power_lower_limit(speeds):
            p_losses = []
            
            # Loop through the route segments
            for i in range(len(speeds)):
                v_guess = speeds[i]
                theta = route_inclines[i]
                
                F1 = self.aerodynamic_drag(
                    v_guess, 
                    car_rotation_per_section[i], 
                    wind_speed,                           # Gathered from weather API
                    car_rotation_per_section[i]+90,       # Gathered from weather API
                    1.225, # air density
                    1.93,  # frontal area
                    0.19   # base drag coefficient
                ) 
                F2 = self.rolling_resistance(theta)
                F3 = self.grav_force(theta)
                
                segment_p_loss = self.power_loss(v_guess, F1, F2, F3)
                p_losses.append(segment_p_loss)
                
            # Find the lowest power draw (usually during steep regenerative braking)
            min_power = min(p_losses)
            
            # Example A: min_power is -3000W -> Returns 2000.0 (Valid)
            # Example B: min_power is -6000W -> Returns -1000.0 (Invalid)
            return min_power - (-5000.0)
            
        constraints.append({'type': 'ineq', 'fun': motor_power_upper_limit})
        constraints.append({'type': 'ineq', 'fun': motor_power_lower_limit})

        # Bounds (Constraint Tau: Speed limits)
        # Speed must be between 11.11 m/s (40 km/h) and 33.33 m/s (120 km/h)
        speed_bounds = [(11.11, 33.33) for _ in range(num_intervals)]

        # Run the SQP Solver
        result = minimize(
            fun=objective, 
            x0=initial_speeds, 
            method='SLSQP', # Sequential Least SQuares Programming (SciPy's SQP)
            bounds=speed_bounds, 
            constraints=constraints,
            options={'disp': True, 'maxiter': 100}
        )
        
        if result.success:
            return result.x # Returns the array of optimal speeds
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