"""
Plot data in 2D quickly in real time

This was hard
"""

import collections
import numpy as np
from multiprocessing import Process, Queue
from functools import partial
from PyQt5.QtWidgets import QApplication
from pyqtgraph.Qt import QtCore
import pyqtgraph as pg


"""
Plot data in real time using Qt framework

Data comes from queue filled by parent task
"""
class _DynamicPlotter():

    def __init__(self, data_queue : Queue, plot_name : str, xlabel : str, ylabel : str, lines : list,
                line_colors : list, sampleinterval=0.0416, timewindow=5, size=(600,350)):
        # Figure out intervals and number of points
        self._interval = int(sampleinterval*1000)
        self._bufsize = int(timewindow/sampleinterval)

        # Use dictionaries to hold each lines data, TODO: should allow index by name
        self.line_colors = line_colors
        self.buffer_dict = dict()
        self.curve_dict = dict()
        self.num_lines = len(lines)
        self.lines = lines

        # Init each line seperately
        for line in lines:
            self.buffer_dict[line] = collections.deque([0.0]*self._bufsize, self._bufsize)

        # used for initialization of plot window
        self.x = np.linspace(-timewindow, 0.0, self._bufsize)
        self.y = np.zeros(self._bufsize, dtype=np.float64)
        self.data_queue = data_queue
        # Set graph configuration options
        pg.setConfigOptions(antialias=False)
        self.app = QApplication([])
        self.plt = pg.plot(title=plot_name, color='b')
        self.plt.resize(*size)
        self.plt.showGrid(x=True, y=True)
        self.plt.setLabel('left', ylabel)
        self.plt.setLabel('bottom', xlabel)
        self.plt.addLegend()

        # Plot each line with each associated color
        for line in lines:
            line_ind = lines.index(line)
            self.curve_dict[line] = self.plt.plot(self.x, self.y, pen=(line_colors[line_ind]), name=line)

        # QTimer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateplot)
        self.timer.start(self._interval)

    def updateplot(self):
        try :
            new_item = self.data_queue.get(block=False)
            for line in self.lines:
                self.buffer_dict[line].append(new_item[line])
                self.curve_dict[line].setData(self.x, self.buffer_dict[line])
            self.app.processEvents()
        except:
            # queue is empty, don't update data
            for line in self.lines:
                self.curve_dict[line].setData(self.x, self.buffer_dict[line])
            self.app.processEvents()

    def run(self):
        self.app.exec_()

"""
Helper to create and run a dynamic plotter in a new process
"""
def run_plotter(data_queue : Queue, plot_name : str, xlabel : str, ylabel : str, lines : list, line_colors : list,
                sample_period : float):

    # create plot
    p = _DynamicPlotter(data_queue=data_queue, plot_name=plot_name, xlabel=xlabel, ylabel=ylabel, lines=lines,
                        line_colors=line_colors, sampleinterval=sample_period)
    p.run()


'''
User facing class to create and run the plotter

TODO: Log data and maybe generate static graph when done
'''
class Plotter2D:

    def __init__(self, name : str, xlabel : str, ylabel : str, lines : list, line_colors : list, fps : int):

        # Setup child process with realtime plotter
        sample_period = float(1/fps)
        self.q = Queue(maxsize=1)
        self.p = Process(target=run_plotter, args=(self.q, name, xlabel, ylabel, lines, line_colors, sample_period,))
        self.p.start()

    # Try and stick item into the queue, if its full, that is ok, we can just ignore it for now
    def plot(self, data : dict):
        try:
            self.q.put(data, block = False)
        except:
            pass


if __name__ == '__main__':
    pass
