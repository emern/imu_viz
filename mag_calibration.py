"""
Assist with calibrating magnetometers
"""

import time
import numpy as np

import components.parser as p
import components.ICM20948 as ICM
import components.lowpass_filter as flt
from components.scatter_plotter3D import ScatterPlotter3D

# Model configuration constants
MODEL_TIMESTEP = 0.01 # 100hz
MODEL_FREQUENCY = 1/MODEL_TIMESTEP
MODEL_LOWPASS_CUTOFF = 10 # 10 hz cutoff
CALIBRATION_TIME = 30

if __name__ == '__main__':

    scatter = ScatterPlotter3D(name='Collected data', fps=24, names=['actual', 'corrected'], colors=[[1, 0, 0, 1], [0, 0, 1, 1]])
    test_imu = ICM.ICM20948(start_char='&')
    parser = p.Parser(dev_name="ICM20948", imu=test_imu)
    filter = flt.RCFilter(cutoff=MODEL_LOWPASS_CUTOFF, sample_time=MODEL_TIMESTEP)

    print("Starting!!!")

    num_plotted = 0
    acc_vec = np.array([0, 0, 0])
    all_items = np.array([[0, 0, 0]])

    t_end = time.time() + CALIBRATION_TIME # 30 second calibration, adjust as needed

    while time.time() < t_end:
        new_data = parser.run()
        if new_data == None:
            continue


        filtered_vals = ICM.ICMRawData.create_from_vector(filter.filter(new_data.convert_to_vector()))
        scatter.plot({'actual' : np.array([[filtered_vals.mag_x, filtered_vals.mag_y, filtered_vals.mag_z]])})
        acc_vec = acc_vec + np.array([filtered_vals.mag_x, filtered_vals.mag_y, filtered_vals.mag_z])
        num_plotted+=1
        all_items = np.concatenate((all_items, np.array([[filtered_vals.mag_x, filtered_vals.mag_y, filtered_vals.mag_z]])), axis=0)

        time.sleep(MODEL_TIMESTEP)

    time.sleep(1) # let the 3D plotter queue empty

    normalized_items = all_items - (acc_vec/num_plotted)
    scatter.plot({'corrected' : normalized_items})
    print(acc_vec/num_plotted)

