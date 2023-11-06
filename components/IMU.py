"""
Generic IMU interface
"""

import numpy as np

class IMUData:

    # Convert all numerical fields to vector for computation
    def convert_to_vector(self):
        pass

    # Create instance from vector
    @classmethod
    def create_from_vector(cls, vector : np.ndarray):
        pass

class IMU:

    # Parse data output from specific IMU
    def parse_data(self, data : str):
        pass


if __name__ == '__main__':
    pass
