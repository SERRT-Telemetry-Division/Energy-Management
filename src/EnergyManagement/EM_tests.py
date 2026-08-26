import unittest
import math
import numpy as np
from collections import deque
from EnergyManagement import EnergyManager, EnvironmentState, VehicleConfig

class TestEnergyManager(unittest.TestCase):
    
    def setUp(self):
        """
        Runs before EVERY test. Initializes a fresh EnergyManager 
        with the base constants from your architecture.
        """
        self.car = VehicleConfig(
            mass=453.592, 
            solar_array_area=5.797, 
            drag_coefficient=0.19, 
            rolling_resistance=0.005, 
            frontal_area=1.93, 
            energy_cap=19440000, 
            n_motor=0.95, 
            n_elec=0.22, 
            p_aux=14.14
        )
        
        self.env = EnvironmentState(
            air_density=1.225, 
            ghi=800.0
        )
        
        self.em = EnergyManager(self.car, self.env)

    # ----------- MECHANICAL FORCES TESTS -----------

    def test_aerodynamic_drag(self):
        # 0.5 * 1.225 * 1.93 * 0.19 * ((20 + 0)^2) = 89.84075
        v = 20.0
        vw = 0.0
        expected_drag = 89.8415
        result = self.em.aerodynamic_drag(v, vw)
        self.assertAlmostEqual(result, expected_drag, places=4, msg="Aerodynamic drag calculation failed.")

    def test_rolling_resistance(self):
        # 0.005 * 453.592 * 9.81 * cos(0) = 22.24868
        theta = 0.0
        expected_rr = 22.2486876
        result = self.em.rolling_resistance(theta)
        self.assertAlmostEqual(result, expected_rr, places=4, msg="Rolling resistance calculation failed.")

    def test_grav_force(self):
        # 453.592 * 9.81 * sin(0.1) ≈ 444.22
        theta = 0.1 # radians
        expected_grav = 453.592 * 9.81 * math.sin(theta)
        result = self.em.grav_force(theta)
        self.assertAlmostEqual(result, expected_grav, places=4, msg="Gravitational force calculation failed.")

    def test_power_loss(self):
        # (20 / 0.95) * (89.84 + 22.25 + 0) + 14.14 ≈ 2373.93
        v_k = 20.0
        F1 = 89.84
        F2 = 22.25
        F3 = 0.0
        expected_loss = (v_k / 0.95) * (F1 + F2 + F3) + 14.14
        result = self.em.power_loss(v_k, F1, F2, F3)
        self.assertAlmostEqual(result, expected_loss, places=4, msg="Power loss calculation failed.")

    # ----------- SOLAR AND BATTERY POWER TESTS -----------

    def test_sun_generated_power(self):
        # 800 * 0.22 * 5.797 = 1020.272
        expected_sun = 1020.272
        result = self.em.sun_generated_power()
        self.assertAlmostEqual(result, expected_sun, places=4, msg="Solar power generation failed.")

    def test_net_battery_energy_flow(self):
        v_k = 20.0
        v = 20.0
        vw = 0.0
        theta = 0.0
        
        # P_sun (1020.272) - P_loss (approx 2373.94) = -1353.66
        # The exact value relies on the precise float outputs of the prior functions
        F1 = self.em.aerodynamic_drag(v, vw)
        F2 = self.em.rolling_resistance(theta)
        F3 = self.em.grav_force(theta)
        expected_loss = self.em.power_loss(v_k, F1, F2, F3)
        expected_net = self.em.sun_generated_power() - expected_loss
        
        result = self.em.net_battery_energy_flow(v_k, v, vw, theta)
        self.assertAlmostEqual(result, expected_net, places=4, msg="Net battery flow calculation failed.")

    # ----------- ACCELERATION ENERGY TESTS -----------

    def test_acc_energy_insufficient_data(self):
        # Should return 0.0 if there are less than 2 readings
        self.em.speed_stack.append(20.0)
        self.assertEqual(self.em.acc_energy(), 0.0, msg="Acc energy should return 0.0 with < 2 speed readings.")

    def test_acc_energy_valid_data(self):
        # Accelerating from 10 m/s to 20 m/s
        # 0.5 * 453.592 * ((20^2) - (10^2)) = 68038.8 Joules
        self.em.speed_stack.append(10.0)
        self.em.speed_stack.append(20.0)
        
        expected_acc_energy = 68038.8
        result = self.em.acc_energy()
        
        self.assertAlmostEqual(result, expected_acc_energy, places=4, msg="Acceleration energy failed.")
        # Ensure stack was restored properly
        self.assertEqual(len(self.em.speed_stack), 2, msg="Speed stack was not restored after acc_energy calculation.")

    # ----------- STATE OF CHARGE TESTS -----------

    def test_state_of_charge(self):
        # Simulate 2 intervals of driving
        self.em.p_battery_stack.extend([-1000.0, -1500.0]) # Draining 1000W, then 1500W
        self.em.t_k_stack.extend([60.0, 60.0])             # For 60 seconds each
        self.em.acc_energy_stack.extend([10000.0, 5000.0]) # Acceleration cost
        
        alpha_start = 100.0
        steady_sum = (-1000 * 60) + (-1500 * 60) # -150000 Joules
        accel_sum = 10000 + 5000                 # 15000 Joules
        total_energy_change = steady_sum + accel_sum # -135000 Joules
        
        # (-135000 / 19440000) * 100 = -0.6944% change
        expected_soc = 100.0 + (total_energy_change / 19440000) * 100.0
        
        result = self.em.state_of_charge(alpha_start)
        self.assertAlmostEqual(result, expected_soc, places=4, msg="SoC calculation failed.")

    # ----------- STOCHASTIC EXPECTED VALUES TESTS -----------

    def test_expected_sun_power(self):
        # 50% chance of 1000 W/m2, 50% chance of 600 W/m2 -> Expected GHI = 800
        pmf = [(0.5, 1000.0), (0.5, 600.0)]
        expected_ghi = 800.0
        # Expected sun power = 800 * 0.22 * 5.797 = 1020.272
        expected_power = expected_ghi * self.car.n_elec * self.car.solar_array_area
        
        result = self.em.expected_sun_power(pmf)
        self.assertAlmostEqual(result, expected_power, places=4, msg="Expected PMF Sun Power failed.")

    def test_expected_net_battery_power(self):
        prev_batt = 10000.0
        current_sun = 1500.0
        p_loss = 3000.0
        expected_net = 8500.0
        result = self.em.expected_net_battery_power(prev_batt, current_sun, p_loss)
        self.assertEqual(result, expected_net, msg="Expected iterative net battery power failed.")

    # ----------- OPTIMIZATION (INTEGRATION) TEST -----------

    def test_optimize_route_speeds(self):
        """
        NOTE: This test will ONLY pass once the objective and constraint 
        functions inside optimize_route_speeds are fully implemented 
        with the simulation loop, replacing the placeholders.
        """
        # Create a tiny mock route: 2 segments, 1000 meters each
        route_distances = np.array([1000.0, 1000.0])
        
        # Segment 1 is flat (0 rad), Segment 2 is an uphill (0.05 rad)
        route_inclines = np.array([0.0, 0.05])
        
        # Expected GHI for each segment
        expected_ghi_array = np.array([800.0, 800.0])
        
        alpha_start = 100.0
        target_alpha_end = 98.0
        allowed_driving_time = 100.0 # seconds
        
        # Run the optimizer
        optimal_speeds = self.em.optimize_route_speeds(
            route_distances, 
            route_inclines, 
            expected_ghi_array, 
            alpha_start, 
            target_alpha_end, 
            allowed_driving_time
        )
        
        # 1. Check that the output is an array
        self.assertIsInstance(optimal_speeds, np.ndarray, "Optimizer did not return a numpy array.")
        
        # 2. Check that it generated a speed for both segments
        self.assertEqual(len(optimal_speeds), 2, "Optimizer did not return the correct number of speeds.")
        
        # 3. Check that the speeds obey the safe bounds (11.11 to 33.33 m/s)
        for speed in optimal_speeds:
            self.assertTrue(11.11 <= speed <= 33.33, f"Optimized speed {speed} violates bounds.")

if __name__ == '__main__':
    unittest.main()