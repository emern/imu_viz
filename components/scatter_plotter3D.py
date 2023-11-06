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

    def __init__(self, data_queue : Queue, plot_name : str, names : list, colors : list, sampleinterval=0.0416):
        # Figure out intervals and number of points
        self._interval = int(sampleinterval*1000)
        self.app = QApplication([])
        self.view = gl.GLViewWidget()

        self.data_queue = data_queue
        self.plot_name = plot_name

        self.view.opts['distance'] = 300
        self.view.setWindowTitle(plot_name)
        #self.view.setGeometry(0, 110, 1920, 1080)

        # create the background grids

        # X axis grid
        gx = gl.GLGridItem()
        gx.setSize(x=200, y=200)
        gx.rotate(90, 0, 1, 0)
        gx.translate(-100, 0, 0)
        self.view.addItem(gx)

        # Y axis grid
        gy = gl.GLGridItem()
        gy.rotate(90, 1, 0, 0)
        gy.translate(0, -100, 0)
        gy.setSize(x=200, y=200)
        self.view.addItem(gy)

        # Z axis grid
        gz = gl.GLGridItem()
        gz.translate(0, 0, -100)
        gz.setSize(x=200, y=200)
        self.view.addItem(gz)

        # Plot guide marker, note that our "real world" coordinate scheme is:
        # [North, West, Up]
        self.center = (0,0,0)
        x1 = (5,0,0)
        y1 = (0,5,0)
        z1 = (0,0,5)
        pts_x = np.array([self.center, x1])
        pts_y = np.array([self.center, y1])
        pts_z = np.array([self.center, z1])

        sh1 = gl.GLLinePlotItem(pos=pts_x, width=2, antialias=False, color='r')
        self.view.addItem(sh1)

        sh2 = gl.GLLinePlotItem(pos=pts_y, width=2, antialias=False, color='g')
        self.view.addItem(sh2)

        sh4 = gl.GLLinePlotItem(pos=pts_z, width=2, antialias=False, color='b')
        self.view.addItem(sh4)

        # create scatter plot for every point collection, indexible by the plot name
        self.plots = dict()
        self.plots_data = dict()
        self.plots_colors = dict()

        for name in names:
            self.plots_data[name] = np.array([[0,0,0]])
            self.plots_colors[name] = colors[names.index(name)]
            self.plots[name] = gl.GLScatterPlotItem(pos=self.plots_data[name], size=1, color = self.plots_colors[name], pxMode = False)
            self.view.addItem(self.plots[name])

        #self.points_collected = np.array([[0,0,0]])
        #self.colors = [1, 0, 0, 1]
        self.view.show()

        # QTimer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateplot)
        self.timer.start(self._interval)

    def updateplot(self):
        try:
            new_item = self.data_queue.get(block=False)
            keylist = list(new_item.keys())

            # update plot data for each plot seperately
            for name in keylist:
                self.plots_data[name] = np.concatenate((self.plots_data[name], new_item[name]), axis=0)
                self.plots[name].setData(pos=self.plots_data[name], size=1, color = self.plots_colors[name], pxMode = False)

            self.app.processEvents()
        except:
            self.app.processEvents()

    def run(self):
        self.app.exec_()

"""
Helper to create and run a dynamic plotter in a new process
"""
def run_plotter(data_queue : Queue, plot_name : str, sample_period : float, names : list, colors : list):

    # create plot
    p = _DynamicPlotter(data_queue=data_queue, plot_name=plot_name, sampleinterval=sample_period, names=names, colors=colors)
    p.run()


'''
User facing class to create and run the plotter

TODO: Log data and maybe generate static graph when done
'''
class ScatterPlotter3D:

    def __init__(self, name : str, fps : int, names : list, colors : list):

        # Setup child process with realtime plotter
        sample_period = float(1/fps)
        self.q = Queue(maxsize=1)
        self.p = Process(target=run_plotter, args=(self.q, name, sample_period, names, colors,))
        self.p.start()

    # Try and stick item into the queue, if its full, that is ok, we can just ignore it for now
    def plot(self, data : dict):
        try:
            self.q.put(data, block = False)
        except:
            pass


