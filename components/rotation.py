"""
Rotation matrix utilities
"""

import numpy as np

class RotationMatrix:

    def __init__(self, a11, a12, a13, a21, a22, a23, a31, a32, a33):
        # Create matrix
        self.matrix = np.array([[ a11, a12, a13],
                                [ a21, a22, a23],
                                [ a31, a32, a33]])

    """
    Build rotation matrix to transform body rates about "x" axis to intertial frame rates in the form:

    [phi, theta, sigma]^T
    """
    @classmethod
    def build_rotation_x(cls, angle : float):
        pass

    def calc_vec(self, invec : np.ndarray) -> np.ndarray:
        return np.matmul(self.matrix, invec)
