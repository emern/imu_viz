"""
Basic complementary filter
"""

import numpy as np
from components.IMU import IMUData
from components.rotation import RotationMatrix

class ComplementaryFilter:

    def __init__(self, alpha : float):
        self.alpha = alpha


    def estimate(self, accel_data : np.ndarray, mag_data : np.ndarray) -> IMUData:

        # First we normalize acclerometer and magnetometer readings
        accel_unit = accel_data / np.linalg.norm(accel_data)
        mag_unit = mag_data / np.linalg.norm(mag_data)

        # West (y) is negative cross product of downwards acceleration and magnetic field (mag points "north-down")
        y = np.cross(-accel_unit, mag_unit)
        y = -y / np.linalg.norm(y)

        # X direction (Magnetic North) is cross product of East (- West) and Down
        x = np.cross(-y, -accel_unit)
        x = x / np.linalg.norm(x)

        # Up (z) is accel z
        z = accel_unit

        # construct rotation matrix -> [X, Y, Z]
        self.last_estimate = RotationMatrix(x[0], y[0], z[0],
                                            x[1], y[1], z[1],
                                            x[2], y[2], z[2])

        return self.last_estimate
