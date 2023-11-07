"""
Implement attitude estimation model for ICM20948
"""

import time

import components.parser as p
import components.ICM20948 as ICM
import components.plotter2D as plt2D
import components.lowpass_filter as flt
from components.complementary_filter import ComplementaryFilter
from components.plotter3D import Plotter3D

# Model configuration constants
MODEL_TIMESTEP = 0.01 # 100hz
MODEL_FREQUENCY = 1/MODEL_TIMESTEP
MODEL_LOWPASS_CUTOFF = 10 # 10 hz cutoff

if __name__ == '__main__':

    #plotter_ac = plt2D.Plotter2D(name='acceleration data', ylabel='acceleration (mg)', xlabel='time (s)',
    #                            lines=['acc_z', 'acc_z_flt'], line_colors=['r', 'g'], fps=24)
    #plotter_gy = plt2D.Plotter2D(name='gyro data', ylabel='rotation (dps)', xlabel='time (s)',
    #                            lines=['gyr_z', 'gyr_z_flt'], line_colors=['r', 'g'], fps=24)
    plotter_ma = plt2D.Plotter2D(name='magnetometer data', ylabel='field (uT)', xlabel='time (s)',
                                lines=['mag_x_flt', 'mag_y_flt','mag_z_flt'], line_colors=['r', 'g', 'b'], fps=24)

    visualizer = Plotter3D('Rotational state', 24)
    test_imu = ICM.ICM20948(start_char='&')
    parser = p.Parser(dev_name="ICM20948", imu=test_imu, port='COM5', baud=115200)
    filter = flt.RCFilter(cutoff=MODEL_LOWPASS_CUTOFF, sample_time=MODEL_TIMESTEP)

    estimator = ComplementaryFilter(alpha=0.1)

    while True:
        new_data = parser.run()
        if new_data == None:
            continue


        filtered_vals = ICM.ICMRawData.create_from_vector(filter.filter(new_data.convert_to_vector()))
        #plotter_ac.plot({'acc_z' : new_data.ac_z, 'acc_z_flt' : filtered_vals.ac_z})
        #plotter_gy.plot({'gyr_z' : new_data.gyr_z, 'gyr_z_flt' : filtered_vals.gyr_z})
        plotter_ma.plot({'mag_x_flt' : filtered_vals.mag_x, 'mag_y_flt' : filtered_vals.mag_y, 'mag_z_flt' : filtered_vals.mag_z})

        estimate_matrix = estimator.estimate(accel_data=filtered_vals.get_raw_accel(), mag_data=filtered_vals.get_adjusted_mag())
        visualizer.plot(estimate_matrix)

        time.sleep(MODEL_TIMESTEP)


