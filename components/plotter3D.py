"""
Plot data in 2D quickly in real time

This was hard
"""

import numpy as np
from multiprocessing import Process, Queue
from functools import partial
from PyQt5.QtWidgets import QApplication
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore
import pyqtgraph as pg


"""
Plot data in real time using Qt framework

Data comes from queue filled by parent task
"""
class _DynamicPlotter():

    def __init__(self, data_queue : Queue, plot_name : str, sampleinterval=0.0416):
        # Figure out intervals and number of points
        self._interval = int(sampleinterval*1000)
        self.app = QApplication([])
        self.view = gl.GLViewWidget()

        self.data_queue = data_queue
        self.plot_name = plot_name

        self.view.opts['distance'] = 20
        self.view.setWindowTitle(plot_name)
        #self.view.setGeometry(0, 110, 1920, 1080)

        # create the background grids

        # X axis grid
        gx = gl.GLGridItem()
        gx.setSize(x=10, y=10)
        gx.rotate(90, 0, 1, 0)
        gx.translate(-5, 0, 0)
        self.view.addItem(gx)

        # Y axis grid
        gy = gl.GLGridItem()
        gy.rotate(90, 1, 0, 0)
        gy.translate(0, -5, 0)
        gy.setSize(x=10, y=10)
        self.view.addItem(gy)

        # Z axis grid
        gz = gl.GLGridItem()
        gz.translate(0, 0, -5)
        gz.setSize(x=10, y=10)
        self.view.addItem(gz)

        # Plot guide marker, note that our "real world" coordinate scheme is:
        # [North, East, Down]
        self.center = (0,0,0)
        x1 = (1,0,0)
        y1 = (0,1,0)
        z1 = (0,0,1)
        pts_x = np.array([self.center, x1])
        pts_y = np.array([self.center, y1])
        pts_z = np.array([self.center, z1])

        sh1 = gl.GLLinePlotItem(pos=pts_x, width=2, antialias=False, color='r')
        self.view.addItem(sh1)

        sh2 = gl.GLLinePlotItem(pos=pts_y, width=2, antialias=False, color='g')
        self.view.addItem(sh2)

        sh4 = gl.GLLinePlotItem(pos=pts_z, width=2, antialias=False, color='b')
        self.view.addItem(sh4)

        # Create moving object
        self.x_vec = gl.GLLinePlotItem(pos=pts_x, width=1, antialias=False, color='r')
        self.y_vec = gl.GLLinePlotItem(pos=pts_y, width=1, antialias=False, color='g')
        self.z_vec = gl.GLLinePlotItem(pos=pts_z, width=1, antialias=False, color='b')
        self.view.addItem(self.x_vec)
        self.view.addItem(self.y_vec)
        self.view.addItem(self.z_vec)

        self.view.show()

        # QTimer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateplot)
        self.timer.start(self._interval)

    def updateplot(self):
        try :
            new_item = self.data_queue.get(block=False)

            # Calculate new vectors from elementary X, Y and Z vectors
            xvec_new = tuple(new_item.calc_vec(np.array([1,0,0])))
            yvec_new = tuple(new_item.calc_vec(np.array([0,1,0])))
            zvec_new = tuple(new_item.calc_vec(np.array([0,0,1])))

            pts_x = np.array([self.center, xvec_new])
            pts_y = np.array([self.center, yvec_new])
            pts_z = np.array([self.center, zvec_new])

            self.x_vec.setData(pos=pts_x, width=1, color='r')
            self.y_vec.setData(pos=pts_y, width=1, antialias=False, color='g')
            self.z_vec.setData(pos=pts_z, width=1, antialias=False, color='b')

            self.app.processEvents()
        except:
            self.app.processEvents()

    def run(self):
        self.app.exec_()

"""
Helper to create and run a dynamic plotter in a new process
"""
def run_plotter(data_queue : Queue, plot_name : str, sample_period : float):

    # create plot
    p = _DynamicPlotter(data_queue=data_queue, plot_name=plot_name, sampleinterval=sample_period)
    p.run()


'''
User facing class to create and run the plotter

TODO: Log data and maybe generate static graph when done
'''
class Plotter3D:

    def __init__(self, name : str, fps : int):

        # Setup child process with realtime plotter
        sample_period = float(1/fps)
        self.q = Queue(maxsize=1)
        self.p = Process(target=run_plotter, args=(self.q, name, sample_period,))
        self.p.start()

    # Try and stick item into the queue, if its full, that is ok, we can just ignore it for now
    def plot(self, data : dict):
        try:
            self.q.put(data, block = False)
        except:
            pass


if __name__ == '__main__':
    pass

