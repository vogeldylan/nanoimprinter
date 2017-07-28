'''
    ********************************************************************************************************************
    *   FILE NAME:      dataLogClass.py
    *   AUTHOR:         Yu Dong (Peter) Feng, Dylan Vogel
    *   PURPOSE:        This file contains the dataLog class, which is used for creating & updating data files and graphs
    ********************************************************************************************************************
'''

import os
import time

import matplotlib
matplotlib.use('qt5agg')
import matplotlib.pyplot as plt
import datetime


from matplotlib.figure import Figure

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

#
from PyQt5 import QtGui
from PyQt5.QtWidgets import QVBoxLayout

class dataLog:
    def __init__(self, label):
        #Setup the directory that the files will be stored in
        self.localTime = time.localtime()
        self.dir_name = str(self.localTime.tm_year) + '-' + str(self.localTime.tm_mon) + '-' + str(self.localTime.tm_mday)
        self.setup(label)

    def setup(self, label):

        if not os.path.exists(self.dir_name):
            os.makedirs(self.dir_name)
            os.chmod(self.dir_name, 0o777)

        #Setup the file
        self.file_name = label + '-' + str(self.localTime.tm_hour) + '-' + str(self.localTime.tm_min) + '-' + str(self.localTime.tm_sec)
        self.datafile = open(self.dir_name + '/' + self.file_name, 'a')

    def write(self, type, data, message):
        ''' Valid types (thus far):
            COL
            LINE
        '''
        if (type == 'COL'):
            for i in range(0, len(data)):
                self.datafile.write(message[i] + str(data[i]) + '\t')
            self.datafile.write('\n')
        elif (type == 'LINE'):
            self.datafile.write(message + str(data) + '\n')


    def createPlot(self, window):

        window.graphWidget.figure = Figure(figsize = (5, 4), dpi = 100)
        window.graphWidget.canvas = FigureCanvas(window.graphWidget.figure)
        window.graphWidget.toolbar = NavigationToolbar(window.graphWidget.canvas, window)
        window.graphWidget.layout = QVBoxLayout()
        window.graphWidget.layout.addWidget(window.graphWidget.toolbar)
        window.graphWidget.layout.addWidget(window.graphWidget.canvas)
        window.graphWidget.setLayout(window.graphWidget.layout)

        # instead of ax.hold(False)
        window.graphWidget.figure.clear()

        # create an axis
        window.graphWidget.canvas.ax = window.graphWidget.figure.add_subplot(111)


        # plot data
        target_temps = []
        for i in range(0, len(window.process.times)):
            target_temps.append(float(window.process.temp))

        window.graphWidget.ax.plot(window.process.times, window.process.cent_temps, 'r', label = 'Center Temp')
        window.graphWidget.ax.plot(window.process.times, window.process.edge_temps, 'b', label = 'Edge Temp')
        window.graphWidget.ax.plot(window.process.times, target_temps, 'y', label = 'Target Temp')
        window.graphWidget.ax.set_xlabel('Time From Start (s)')
        window.graphWidget.ax.set_ylabel('Temperature (°C)')
        window.graphWidget.ax.set_title('Temperature Measurements Over Time For Heating Test ')
        window.graphWidget.canvas.ax.set_ylim([0, float(window.process.temp) + 30])
        window.graphWidget.ax.legend(loc='lower left', shadow = True)


        #change
        window.graphWidget.ax.set_ylim([0, float(window.process.temp) + 30])

        # refresh canvas
        window.graphWidget.canvas.draw()
        window.update()



    def createPlotTemp(self, window):
        #Create graph for the temperature mode

        #Get current time and date
        #now = datetime.datetime.now()

        #Setup the figure and the canvas for the graph
        window.graphWidget.figure = plt.figure()
        window.graphWidget.canvas = FigureCanvas(window.graphWidget.figure)
        window.graphWidget.toolbar = NavigationToolbar(window.graphWidget.canvas, window)
        window.graphWidget.layout = QVBoxLayout()
        window.graphWidget.layout.addWidget(window.graphWidget.toolbar)
        window.graphWidget.layout.addWidget(window.graphWidget.canvas)
        window.graphWidget.setLayout(window.graphWidget.layout)

        # instead of ax.hold(False)
        window.graphWidget.figure.clear()

        # create an axis
        window.graphWidget.ax = window.graphWidget.figure.add_subplot(111)

        #Plot data
        window.graphWidget.ax.plot(window.process.times, window.process.cent_temps, 'r', window.process.times, window.process.edge_temps, 'b')
        window.graphWidget.ax.set_xlabel('Time From Start (s)')
        window.graphWidget.ax.set_ylabel('Temperature (°C)')
        window.graphWidget.ax.set_title('Temperature Measurements Over Time ')

        # refresh canvas
        window.graphWidget.canvas.draw()
        window.update()

    def updatePlot(self, window):
        #Refresh the graph
        window.graphWidget.canvas.ax.clear()

        target_temps = []
        for i in range(0, len(window.process.times)):
            target_temps.append(float(window.process.temp))

        window.graphWidget.ax.plot(window.process.times, window.process.cent_temps, 'r', label = 'Center Temp')
        window.graphWidget.ax.plot(window.process.times, window.process.edge_temps, 'b', label = 'Edge Temp')
        window.graphWidget.ax.plot(window.process.times, target_temps, 'y', label = 'Target Temp')
        window.graphWidget.ax.set_xlabel('Time From Start (s)')
        window.graphWidget.ax.set_ylabel('Temperature (°C)')
        window.graphWidget.ax.set_title('Temperature Measurements Over Time For Heating Test ')
        window.graphWidget.canvas.ax.set_ylim([0, float(window.process.temp) + 30])
        window.graphWidget.ax.legend(loc='lower left', shadow = True)

        #Refresh the canvas
        window.graphWidget.canvas.draw()
        window.update()


    def updatePlotTemp(self, window):
        #Refresh the graph
        window.graphWidget.canvas.ax.clear()


        window.graphWidget.ax.plot(window.process.times, window.process.cent_temps, 'r', label = 'Center Temp')
        window.graphWidget.ax.plot(window.process.times, window.process.edge_temps, 'b', label = 'Edge Temp')
        window.graphWidget.ax.set_xlabel('Time From Start (s)')
        window.graphWidget.ax.set_ylabel('Temperature (°C)')
        window.graphWidget.ax.set_title('Temperature Measurements Over Time ')
        window.graphWidget.ax.legend(loc='lower left', shadow = True)

        #Refresh the canvas
        window.graphWidget.canvas.draw()
        window.update()

    def savePlot(self, window):
        now = datetime.datetime.now()

        #Create strings to describe the PID setup for the center and edge thermocouples
        original_center_string = "(" + str(window.process.pid_center_val['P']) + "," + str(
            window.process.pid_center_val['I']) + "," + str(window.process.pid_center_val['D']) + ")"

        new_center_string = "(" + str(window.process.coefficients_center['P']) + "," + str(window.process.coefficients_center['I']) + "," + str(
            window.process.coefficients_center['D']) + ")"

        original_edge_string = "(" + str(window.process.pid_edge_val['P']) + "," + str(window.process.pid_edge_val['I']) + "," + str(
            window.process.pid_edge_val['D']) + ")"

        new_edge_string = "(" + str(window.process.coefficients_edge['P']) + "," + str(window.process.coefficients_edge['I']) + "," + str(
            window.process.coefficients_edge['D']) + ")"

        pid_center_string = "center - [" + original_center_string + "," + new_center_string + "]"
        pid_edge_string = "edge - [" + original_edge_string + "," + new_edge_string + "]"


        #The original pdf that will be saved as a pdf
        fig_original = plt.figure()
        fig_original.set_size_inches(12, 10)

        plt.plot(window.process.times, window.process.cent_temps, 'r', window.process.times, window.process.edge_temps, 'b')
        plt.ylabel('Temperature (°C)')
        plt.xlabel('Time From Start (s)')
        plt.title('Heating Characteristics for ' + pid_center_string + ' ' + pid_edge_string)

        # saving the figure with a formatted name that includes information about the PID setup and the time and date
        fig_original.savefig(pid_center_string + pid_edge_string + now.strftime("%I:%M%p - %B %d - %Y") + '-graph.pdf')


    def savePlotTemp(self, window):
        #Save the graph as a PDF
        now = datetime.datetime.now()

        fig_original = plt.figure()
        fig_original.set_size_inches(12, 10)

        plt.plot(window.process.times, window.process.cent_temps, 'r', label = 'Center Temp')
        plt.plot(window.process.times, window.process.edge_temps, 'b', label = 'Edge Temp')
        plt.legend(loc='lower left', shadow=True)
        plt.ylabel('Temperature (°C)')
        plt.xlabel('Time From Start (s)')
        plt.title('Temperature Measurements Over Time ')

        #Save the graph with a formatted name that includes information about the PID setup and the time and date
        fig_original.savefig(now.strftime("%I:%M%p - %B %d - %Y") + '-temperature graph.pdf')


    def write_line_to_log(self, window): #change
        #Add the time, temperature, and duty to the datalog for heating mode
        d_time = round((window.process.curr_t - window.process.start_t), 2)

        window.process.times.append(d_time)
        window.process.cent_temps.append(window.process.t_center)
        window.process.edge_temps.append(window.process.t_edge)

        self.write('COL', [d_time, window.process.t_center, window.process.t_edge, round(window.process.pwm_center, 3), round(window.process.pwm_edge, 3)],
              ['Time: ', 'Temp_1: ', 'Temp_2: ', 'Duty_center: ', 'Duty_edge: '])


        window.displayMessage('[Time: ' + str(d_time) + ']')
        window.outputMessage.setTextColor(QtGui.QColor(255, 0, 0))
        window.displayMessage('[Temp_1: ' + str(window.process.t_center) + ']   ' + '[Duty_center: ' + str(round(window.process.pwm_center, 3)) + ']')
        window.outputMessage.setTextColor(QtGui.QColor(0, 0, 255))
        window.displayMessage('[Temp_2: ' + str(window.process.t_edge) + ']   ' + '[Duty_edge: ' + str(round(window.process.pwm_edge, 3)) + "]")
        window.outputMessage.setTextColor(QtGui.QColor(0, 0, 0))
        window.displayMessage('-------------------------------------------------------')

    def write_temp_to_log(self, window):
        #Add the time and temperature to the datalog for the temperature mode
        d_time = round((window.process.curr_t - window.process.start_t), 2)

        window.process.times.append(d_time)
        window.process.cent_temps.append(window.process.t_center)
        window.process.edge_temps.append(window.process.t_edge)
        self.write('COL', [d_time, window.process.t_center, window.process.t_edge], ['Time: ', ' Temp_1: ', 'Temp_2'])
        #window.displayMessage('[Time: ' + str(d_time) + ']\t' + '[Temp_1: ' + str(window.process.t_center) + ']\t' + 'Temp_2: ' + str(window.process.t_edge) + ']\t')
        window.displayMessage('[Time: ' + str(d_time) + ']')
        window.outputMessage.setTextColor(QtGui.QColor(255, 0, 0))
        window.displayMessage('[Temp_1: ' + str(window.process.t_center) + ']')
        window.outputMessage.setTextColor(QtGui.QColor(0, 0, 255))
        window.displayMessage('Temp_2: ' + str(window.process.t_edge) + ']')
        window.outputMessage.setTextColor(QtGui.QColor(0, 0, 0))
        window.displayMessage('-------------------------------------------------------')


    def close(self):
        #Close the datalog
        self.datafile.close()
