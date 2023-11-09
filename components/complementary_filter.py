"""
Basic complementary filter
"""

import numpy as np
import math as m
from components.rotation import RotationMatrix
import time
from scipy.spatial.transform import Rotation as R

class ComplementaryFilter:

    def __init__(self, alpha : float, time_step : float):
        self.alpha = alpha
        self.time_step = time_step
        self.first_estimate_done = False
        self.last_estimate = None
        self.missing_steps = 0

    """
    Return in terms of Quaternions
    """
    def _accel_mag_model(self, accel_data : np.ndarray, mag_data : np.ndarray) -> np.ndarray:

        accel_unit = accel_data / np.linalg.norm(accel_data)
        mag_unit = mag_data / np.linalg.norm(mag_data)

        # East (y) is cross product of downwards acceleration and magnetic field (mag points "north-down")
        y =  np.cross(-accel_unit, mag_unit)
        y = y / np.linalg.norm(y)

        # North (x) is cross product of East (y) and down (z)
        x = np.cross(y, -accel_unit)
        x = x / np.linalg.norm(x)

        # Down (z) is negative accel z
        z = -accel_unit

        # construct rotation matrix -> [X, Y, Z]
        rot =  R.from_matrix([[x[0], y[0], z[0]],
                                [x[1], y[1], z[1]],
                                [x[2], y[2], z[2]]])
        items = rot.as_quat() # comes out as x,y,z,w format
        return np.array([items[3], items[0], items[1], items[2]])

    """
    Based on aproach described here: https://lucidar.me/en/quaternions/quaternion-and-gyroscope/
    """
    def _gyro_dead_reckoning(self, gyro_data : np.ndarray):
        gyro_data_rad = gyro_data * (m.pi/ 180)
        s_w = np.array([0, gyro_data_rad[0], gyro_data_rad[1], gyro_data_rad[2]])
        dq = RotationMatrix.quat_multiply(0.5 * self.last_estimate, s_w)
        t_delta = time.time() - self.last_time
        q_next = self.last_estimate + (dq * t_delta)
        return q_next

    def estimate(self, accel_data : np.ndarray, mag_data : np.ndarray, gyro_data : np.ndarray) -> RotationMatrix:

        # We need an existing model estimate to be able to factor gyro readings for proper complementary filter
        if self.first_estimate_done == False:
            self.last_estimate = np.array([1, 0, 0, 0])
            self.first_estimate_done = True
            self.last_time = time.time()
            return RotationMatrix.quaternion_rotation_matrix(self.last_estimate)

        # First we do the gyro integration and estimation
        gyro_angles_estimate = self._gyro_dead_reckoning(gyro_data=gyro_data)
        gyro_angles_estimate = gyro_angles_estimate / np.linalg.norm(gyro_angles_estimate)

        # Next we find the accelerometer/magnetometer readings
        accel_mag_estimate = self._accel_mag_model(accel_data=accel_data, mag_data=mag_data)
        accel_mag_estimate = accel_mag_estimate / np.linalg.norm(accel_mag_estimate)

        # Find complementary filter
        total = (1-self.alpha) * gyro_angles_estimate + (self.alpha * accel_mag_estimate)

        self.last_estimate = total / np.linalg.norm(total)
        self.last_time = time.time()

        return RotationMatrix.quaternion_rotation_matrix(self.last_estimate)

