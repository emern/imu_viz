"""

Device specific configuration and implementation for ICM-20948 IMU

"""

import re
import components.IMU
import numpy as np


MAG_SOFT_IRON_ADJUSTMENT = np.array([ 11.82052489, -11.0642615, 46.75668695])

"""
Data and operations for ICM20948 IMU data
"""
class ICMRawData(components.IMU.IMUData):

    def __init__(self, ac_x, ac_y, ac_z, gyr_x, gyr_y, gyr_z, mag_x, mag_y, mag_z) -> None:
        self.ac_x = ac_x
        self.ac_y = ac_y
        self.ac_z = ac_z
        self.gyr_x = gyr_x
        self.gyr_y = gyr_y
        self.gyr_z = gyr_z
        self.mag_x = mag_x
        self.mag_y = mag_y
        self.mag_z = mag_z

        self.has_been_vectorized = False
        self.vectorized_data = None

    """
    Convert relevant IMU data into a vector for fast processing
    """
    def convert_to_vector(self) -> np.ndarray:
        # First check if the data has already been vectorized
        if self.has_been_vectorized == True:
            return self.vectorized_data

        # If not, we must do it here
        self.vectorized_data = np.array([self.ac_x,
                                        self.ac_y,
                                        self.ac_z,
                                        self.gyr_x,
                                        self.gyr_y,
                                        self.gyr_z,
                                        self.mag_x,
                                        self.mag_y,
                                        self.mag_z,])
        self.has_been_vectorized = True
        return self.vectorized_data

    # Create instance from vector
    @classmethod
    def create_from_vector(cls, vector : np.ndarray):
        return cls(vector[0],
                    vector[1],
                    vector[2],
                    vector[3],
                    vector[4],
                    vector[5],
                    vector[6],
                    vector[7],
                    vector[8])

    # Get magnetometer data as x,y,z array
    def get_raw_mag(self) -> np.ndarray:
        return np.array([self.mag_x, self.mag_y, self.mag_z])

    # Get mag data adjusted for soft iron disturbances
    def get_adjusted_mag(self) -> np.ndarray:
        return np.array([self.mag_x, self.mag_y, self.mag_z]) - MAG_SOFT_IRON_ADJUSTMENT

    # Get accelerometer data as x,y,z array
    def get_raw_accel(self) -> np.ndarray:
        return np.array([self.ac_x, self.ac_y, self.ac_z])

    # Get gyro rates in x,y,z axis
    def get_raw_gyro(self) -> np.ndarray:
        return np.array([self.gyr_x, self.gyr_y, self.gyr_z])




class ICM20948(components.IMU.IMU):

    def __init__(self, start_char : str):
        self.start_char = start_char

    def parse_data(self, data : str):

        # check start character, don't do expensive regex operations if it is not correct
        if len(data) > 0 and data[0] != self.start_char:
            return None

        # parse incoming string
        search_str = "(-?\\d+(\\.\\d*)?|\\.\\d+)([eE][-+]?\\d+)?, "
        try:
            results = list(re.findall(search_str, data))
        except:
            return None

        # Dispatch to IMU data holder
        try:
            return ICMRawData(float(results[0][0]),
                            float(results[1][0]),
                            float(results[2][0]),
                            float(results[3][0]),
                            float(results[4][0]),
                            float(results[5][0]),
                            float(results[6][0]),
                            float(results[7][0]),
                            float(results[8][0]))
        except:
            # something went wrong
            return None

if __name__ == '__main__':
    pass
