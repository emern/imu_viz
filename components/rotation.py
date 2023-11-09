"""
Rotation matrix utilities
"""

import numpy as np
import math as m

class RotationMatrix:

    def __init__(self, a11, a12, a13, a21, a22, a23, a31, a32, a33):
        # Create matrix
        self.matrix = np.array([[ a11, a12, a13],
                                [ a21, a22, a23],
                                [ a31, a32, a33]])

    def calc_vec(self, invec : np.ndarray) -> np.ndarray:
        return np.matmul(self.matrix, invec)

    @classmethod
    def quaternion_rotation_matrix(cls, quaternion):
        """
        Covert a quaternion into a full three-dimensional rotation matrix.

        Input
        :param Q: A 4 element array representing the quaternion (q0,q1,q2,q3)

        Output
        :return: A rotation matrix

        Credit to: https://automaticaddison.com/how-to-convert-a-quaternion-to-a-rotation-matrix/
        """
        # Extract the values from Q
        q0 = quaternion[0]
        q1 = quaternion[1]
        q2 = quaternion[2]
        q3 = quaternion[3]

        # First row of the rotation matrix
        r00 = 2 * (q0 * q0 + q1 * q1) - 1
        r01 = 2 * (q1 * q2 - q0 * q3)
        r02 = 2 * (q1 * q3 + q0 * q2)

        # Second row of the rotation matrix
        r10 = 2 * (q1 * q2 + q0 * q3)
        r11 = 2 * (q0 * q0 + q2 * q2) - 1
        r12 = 2 * (q2 * q3 - q0 * q1)

        # Third row of the rotation matrix
        r20 = 2 * (q1 * q3 - q0 * q2)
        r21 = 2 * (q2 * q3 + q0 * q1)
        r22 = 2 * (q0 * q0 + q3 * q3) - 1

        # 3x3 rotation matrix
        return cls(r00,
                    r01,
                    r02,
                    r10,
                    r11,
                    r12,
                    r20,
                    r21,
                    r22)

    def get_quaternion(self) -> np.ndarray:
        r = np.sqrt(float(1)+self.matrix[0,0]+self.matrix[1,1]+self.matrix[2,2])*0.5
        i = (self.matrix[2,1]-self.matrix[1,2])/(4*r)
        j = (self.matrix[0,2]-self.matrix[2,0])/(4*r)
        k = (self.matrix[1,0]-self.matrix[0,1])/(4*r)

        return np.array([r, i, j, k])

    """
    Multiply quaternions qp

    Credit to https://stanford.edu/class/ee267/lectures/lecture10.pdf
    """
    @staticmethod
    def quat_multiply(quaternion0, quaternion1):

        qw = quaternion0[0]
        qx = quaternion0[1]
        qy = quaternion0[2]
        qz = quaternion0[3]

        pw = quaternion1[0]
        px = quaternion1[1]
        py = quaternion1[2]
        pz = quaternion1[3]

        return np.array([
            qw*pw - qx*px - qy*py - qz*pz,
            qw*px + qx*pw + qy*pz - qz*py,
            qw*py - qx*pz + qy*pw + qz*px,
            qw*pz + qx*py - qy*px + qz*pw
        ])
