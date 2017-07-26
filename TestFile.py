import sys
from PyQt5 import QtGui, QtWidgets, QtCore, uic
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QVBoxLayout
from PyQt5.QtCore import QCoreApplication

import pid_setup


import dataLog as log
import thmcouple as thm
import heater

import traceback
import PID
import time

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import random

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('heaterGUInewtest.ui', self)
        self.setUp()
        self.temp = 0
        self.P_center = 0
        self.I_center = 0
        self.D_center = 0
        self.P_edge = 0
        self.I_edge = 0
        self.D_edge = 0
        #self.show()

    def setUp(self):

        self.outputMessage.append("Welcome to ")
        self.outputMessage.append('[Time: ' + "a]" + '[Temp_1: ' + "b]" + '[Temp_2: ' + "c]" + '\n[Duty_center: ' +"d]" + '[Duty_edge: ' + "e]")
        self.runButton.clicked.connect(self.handleRun)
        self.stopButton.clicked.connect(self.handleStop)
        self.stopButton.setEnabled(False)

        '''
        self.graphWidget.figure = plt.figure()
        self.graphWidget.canvas = FigureCanvas(self.graphWidget.figure)
        self.graphWidget.toolbar = NavigationToolbar(self.graphWidget.canvas, self)

        self.graphWidget.layout = QVBoxLayout()
        self.graphWidget.layout.addWidget(self.graphWidget.toolbar)
        self.graphWidget.layout.addWidget(self.graphWidget.canvas)

        self.graphWidget.setLayout(self.graphWidget.layout)
        data = [random.random() for i in range(10)]

        # instead of ax.hold(False)
        self.graphWidget.figure.clear()

        # create an axis
        self.graphWidget.ax = self.graphWidget.figure.add_subplot(111)

        # discards the old graph
        # ax.hold(False) # deprecated, see above

        # plot data
        self.graphWidget.ax.plot(data, '*-')

        # refresh canvas
        self.graphWidget.canvas.draw()
        '''

    def handleRun(self):
        '''
        statusTemp = self.checkTemp()
        if(statusTemp == "enter a temperature"):
            self.generateMessageBox("Enter Temperature", "Please enter a temperature value")
        elif(statusTemp == "temperature too high"):
            self.generateMessageBox("Temperature too high", "The temperature value entered is too high. Please enter a value below 200.")
        elif(statusTemp == "invalid temperature"):
            self.generateMessageBox("Invalid temperature", "Please enter a valid temperature")
        elif(statusTemp  == "valid temperature"):
            statusP_center = self.checkP("center")
            statusI_center = self.checkI("center")
            statusD_center = self.checkD("center")

            statusP_edge = self.checkP("edge")
            statusI_edge = self.checkI("edge")
            statusD_edge = self.checkD("edge")

            if(statusP_center == "invalid P"):
                self.generateMessageBox("Invalid center P", "The center P value entered is invalid. Please enter a valid value")
            elif(statusP_center == "enter a P"):
                self.generateMessageBox("Enter center P value", "Please enter a center P value.")

            if(statusI_center == "invalid I"):
                self.generateMessageBox("Invalid center I", "The center I value entered is invalid. Please enter a valid value")
            elif(statusI_center == "enter a I"):
                self.generateMessageBox("Enter center I value", "Please enter a center I value.")

            if(statusD_center == "invalid D"):
                self.generateMessageBox("Invalid D", "The center D value entered is invalid. Please enter a valid value")
            elif(statusD_center == "enter a D"):
                self.generateMessageBox("Enter center D value", "Please enter a center D value.")


            if(statusP_edge == "invalid P"):
                self.generateMessageBox("Invalid edge P", "The edge P value entered is invalid. Please enter a valid value")
            elif(statusP_edge == "enter a P"):
                self.generateMessageBox("Enter edge P value", "Please enter an edge P value.")

            if(statusI_edge == "invalid I"):
                self.generateMessageBox("Invalid edge I", "The edge I value entered is invalid. Please enter a valid value")
            elif(statusI_edge == "enter a I"):
                self.generateMessageBox("Enter edge I value", "Please enter an edge I value.")

            if(statusD_edge == "invalid D"):
                self.generateMessageBox("Invalid D", "The edge D value entered is invalid. Please enter a valid value")
            elif(statusD_edge == "enter a D"):
                self.generateMessageBox("Enter edge D value", "Please enter an edge D value.")

            if(statusP_center == "valid P" and statusI_center == "valid I" and statusD_center == "valid D"):
                center_Valid = True
            else:
                center_Valid = False

            if (statusP_edge == "valid P" and statusI_edge == "valid I" and statusD_edge == "valid D"):
                edge_Valid = True
            else:
                edge_Valid = False

            if(center_Valid == True and edge_Valid == True):
                self.temp = float(self.tempEdit.text())
                self.P_center = float(self.pEdit_center.text())
                self.I_center = float(self.iEdit_center.text())
                self.D_center = float(self.dEdit_center.text())
                self.P_edge = float(self.pEdit_edge.text())
                self.I_edge = float(self.iEdit_edge.text())
                self.D_edge = float(self.dEdit_edge.text())
            '''

        inputStatus = self.checkInput()

        if(inputStatus == True):
            self.data_log_freq = 1

            # The PWM duty used for the initial heating. Generally around 50% for the
            # center and 100% for the edge seems to work. Should be adjusted based on
            # changes to the thermal volume based on empirical results.
            self.pwm_center = 40
            self.pwm_edge = 100

            # Used to suppress Kp as it approaches the setpoint.
            self.limited_kp = 1  # heater.calc_kp(work_temp)

            self.limited_kd = -0.2

            # Time to wait after initial heating for temp to settle
            self.wait_time = 30

            ################################################################################
            ''' DON'T EDIT THESE UNLESS YOU KNOW WHAT YOU'RE DOING '''


            log.setup("PID_cartridge_test")

            self.thm1 = thm.setup1()
            self.thm2 = thm.setup2()

            self.pwm_1 = heater.setup1()
            self.pwm_2 = heater.setup2()

            self.pid_edge = pid_setup.pid_setup_edge(self.temp, self.P_edge, self.I_edge, self.D_edge)
            self.pid_center = pid_setup.pid_setup_center(self.temp, self.P_center, self.I_center, self.D_center)

            self.pid_edge_val = self.pid_edge.getPID()
            self.pid_center_val = self.pid_center.getPID()

            # These variables will have current temp values written to them.
            self.t_center = thm.read(self.thm1)
            self.t_edge = thm.read(self.thm2)

            # These variables store the temperature averaged over the last two values.
            self.t_center_avg = self.t_center
            self.t_edge_avg = self.t_edge
            

            # Variables used for timekeeping and data plotting.
            self.start_t = time.time()
            self.curr_t = time.time()

            self.times = []
            self.cent_temps = []
            self.edge_temps = []

            self.outputMessage.append("Setup completed, initial heating  ... ")
            self.outputMessage.update()
            QCoreApplication.processEvents()

            self.runButton.setEnabled(False)
            self.stopButton.setEnabled(True)

            #change
            try:
                # Function stored in heater.py. Algorithm based on empirical results.
                self.heat_time = heater.initial_heating_time(self.t_center, self.t_edge, self.temp, self.thm1, self.thm2)
                heater.change_duty(self.pwm_center, self.pwm_edge, self.pwm_1, self.pwm_2)
                # This is the initial heating.
                while ((time.time() - self.start_t) < self.heat_time):
                    if ((time.time() - self.curr_t) >= self.data_log_freq):
                        self.t_center = thm.read(self.thm1)
                        self.t_edge = thm.read(self.thm2)

                        self.curr_t = time.time()
                        log.write_line_to_log(self.t_center, self.t_edge, self.pwm_center, self.pwm_edge, self.curr_t, self.start_t, self.cent_temps,
                                              self.edge_temps, self.times, self)

                # Update PWM values to zero.
                self.pwm_center = 0
                self.pwm_edge = 0
                heater.change_duty(self.pwm_center, self.pwm_edge, self.pwm_1, self.pwm_2)

                self.outputMessage.append('Initial heating finished...')
                self.outputMessage.update()
                QCoreApplication.processEvents()
                log.write('LINE', round((time.time() - self.start_t), 2), 'Initial heating finished at: ')

                self.pid_start_t = time.time()

                # Wait for the temperature to settle.
                while ((time.time() - self.pid_start_t) < self.wait_time):
                    if ((time.time() - self.curr_t) >= self.data_log_freq):
                        self.t_center = thm.read(self.thm1)
                        self.t_edge = thm.read(self.thm2)

                        self.curr_t = time.time()
                        log.write_line_to_log(self.t_center, self.t_edge, self.pwm_center, self.pwm_edge, self.curr_t, self.start_t, self.cent_temps,
                                              self.edge_temps, self.times, self)

                self.outputMessage.append('PID controller started ...')
                self.outputMessage.update()
                QCoreApplication.processEvents()
                log.write('LINE', round((time.time() - self.start_t), 2), 'PID Controller started at: ')

                working = True
                limited = [[False, False], [False, False]]

                while working:
                    self.t_center_last = self.t_center
                    self.t_edge_last = self.t_edge
                    self.t_center = thm.read(self.thm1)
                    self.t_edge = thm.read(self.thm2)

                    if ((time.time() - self.curr_t) >= self.data_log_freq):
                        self.curr_t = time.time()
                        log.write_line_to_log(self.t_center, self.t_edge, self.pwm_center, self.pwm_edge, self.curr_t, self.start_t, self.cent_temps,
                                              self.edge_temps, self.times, self)

                    self.t_center_avg = (self.t_center + self.t_center_last) / 2.0
                    self.t_edge_avg = (self.t_edge + self.t_edge_last) / 2.0

                    self.pid_center.update(self.t_center_avg)
                    self.pwm_center = self.pid_center.output
                    self.pwm_center = heater.clamp(self.pwm_center, 0, 100)

                    self.pid_edge.update(self.t_edge_avg)
                    self.pwm_edge = self.pid_edge.output
                    self.pwm_edge = heater.clamp(self.pwm_edge, 0, 100)

                    heater.change_duty(self.pwm_center, self.pwm_edge, self.pwm_1, self.pwm_2)

                    # Suppress Kp once the current temp nears the working temp.
                    if ((limited[0][0] == False) and ((self.temp - self.t_center_avg) < 15)):
                        self.outputMessage.append("Kp center suppressed ... ")
                        self.outputMessage.update()
                        QCoreApplication.processEvents()
                        log.write('LINE', 0, 'Kp center suppressed')
                        self.pid_center.setKp(self.limited_kp)
                        limited[0][0] = True

                    if ((limited[1][0] == False) and ((self.temp - self.t_edge_avg) < 15)):
                        self.outputMessage.append("Kp edge suppressed ... ")
                        self.outputMessage.update()
                        QCoreApplication.processEvents()
                        log.write('LINE', 0, 'Kp edge suppressed')
                        self.pid_edge.setKp(self.limited_kp)
                        limited[1][0] = True

                    if ((limited[0][1] == False) and ((self.temp - self.t_center_avg) < 1)):
                        self.outputMessage.append("Kd center suppressed ... ")
                        self.outputMessage.update()
                        QCoreApplication.processEvents()
                        log.write('LINE', 0, 'Kd center suppressed')
                        self.pid_center.setKd(self.limited_kd)
                        limited[0][1] = True

                    if ((limited[1][1] == False) and ((self.temp - self.t_edge_avg) < 1)):
                        self.outputMessage.append("Kd edge suppressed ... ")
                        self.outputMessage.update()
                        QCoreApplication.processEvents()
                        log.write('LINE', 0, 'Kd edge suppressed')
                        self.pid_edge.setKd(self.limited_kd)
                        limited[1][1] = True

                    #change
                    if(time.time() - self.start_t >= 15):
                        working = False


            except KeyboardInterrupt:
                log.close()
                thm.close(self.thm1)
                thm.close(self.thm2)
                heater.close(self.pwm_1)
                heater.close(self.pwm_2)

                coefficients_center = self.pid_center.getPID()
                coefficients_edge = self.pid_edge.getPID()

                log.createPlot(self.times, self.cent_temps, self.edge_temps, self.heat_time, coefficients_center, coefficients_edge,
                               self.pid_center_val, self.pid_edge_val, self)
                sys.exit()


            except:
                traceback.print_exc()
                log.close()
                thm.close(self.thm1)
                thm.close(self.thm2)
                heater.close(self.pwm_1)
                heater.close(self.pwm_2)

                sys.exit()

    def handleStop(self):
        self.runButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        log.close()
        thm.close(self.thm1)
        thm.close(self.thm2)
        heater.close(self.pwm_1)
        heater.close(self.pwm_2)

        coefficients_center = self.pid_center.getPID()
        coefficients_edge = self.pid_edge.getPID()

        self.outputMessage.append("\nThe process has finished. Please ensure everything is turned off.")
        self.outputMessage.update()
        QCoreApplication.processEvents()
        log.createPlot(self.times, self.cent_temps, self.edge_temps, self.heat_time, coefficients_center,
                       coefficients_edge,
                       self.pid_center_val, self.pid_edge_val, self)



    def checkInput(self):
        statusTemp = self.checkTemp()
        if(statusTemp == "enter a temperature"):
            self.generateMessageBox("Enter Temperature", "Please enter a temperature value")
        elif(statusTemp == "temperature too high"):
            self.generateMessageBox("Temperature too high", "The temperature value entered is too high. Please enter a value below 200.")
        elif(statusTemp == "invalid temperature"):
            self.generateMessageBox("Invalid temperature", "Please enter a valid temperature")
        elif(statusTemp  == "valid temperature"):
            statusP_center = self.checkP("center")
            statusI_center = self.checkI("center")
            statusD_center = self.checkD("center")

            statusP_edge = self.checkP("edge")
            statusI_edge = self.checkI("edge")
            statusD_edge = self.checkD("edge")

            if(statusP_center == "invalid P"):
                self.generateMessageBox("Invalid center P", "The center P value entered is invalid. Please enter a valid value")
            elif(statusP_center == "enter a P"):
                self.generateMessageBox("Enter center P value", "Please enter a center P value.")

            if(statusI_center == "invalid I"):
                self.generateMessageBox("Invalid center I", "The center I value entered is invalid. Please enter a valid value")
            elif(statusI_center == "enter a I"):
                self.generateMessageBox("Enter center I value", "Please enter a center I value.")

            if(statusD_center == "invalid D"):
                self.generateMessageBox("Invalid D", "The center D value entered is invalid. Please enter a valid value")
            elif(statusD_center == "enter a D"):
                self.generateMessageBox("Enter center D value", "Please enter a center D value.")


            if(statusP_edge == "invalid P"):
                self.generateMessageBox("Invalid edge P", "The edge P value entered is invalid. Please enter a valid value")
            elif(statusP_edge == "enter a P"):
                self.generateMessageBox("Enter edge P value", "Please enter an edge P value.")

            if(statusI_edge == "invalid I"):
                self.generateMessageBox("Invalid edge I", "The edge I value entered is invalid. Please enter a valid value")
            elif(statusI_edge == "enter a I"):
                self.generateMessageBox("Enter edge I value", "Please enter an edge I value.")

            if(statusD_edge == "invalid D"):
                self.generateMessageBox("Invalid D", "The edge D value entered is invalid. Please enter a valid value")
            elif(statusD_edge == "enter a D"):
                self.generateMessageBox("Enter edge D value", "Please enter an edge D value.")

            if(statusP_center == "valid P" and statusI_center == "valid I" and statusD_center == "valid D"):
                center_Valid = True
            else:
                center_Valid = False

            if (statusP_edge == "valid P" and statusI_edge == "valid I" and statusD_edge == "valid D"):
                edge_Valid = True
            else:
                edge_Valid = False

            if(center_Valid == True and edge_Valid == True):
                self.temp = float(self.tempEdit.text())
                self.P_center = float(self.pEdit_center.text())
                self.I_center = float(self.iEdit_center.text())
                self.D_center = float(self.dEdit_center.text())
                self.P_edge = float(self.pEdit_edge.text())
                self.I_edge = float(self.iEdit_edge.text())
                self.D_edge = float(self.dEdit_edge.text())
                return True
            else:
                return False

    def generateMessageBox(self, title, msg):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setWindowTitle(title)
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msgBox.setText(msg)
        msgBox.exec_()

    def checkTemp(self):
        if (self.tempEdit.text() != ''):
            if (self.isTextNumber(self.tempEdit.text()) == True):
                if (float(self.tempEdit.text()) > 200):
                    return("temperature too high")  # output that the input is too high
                else:
                    return("valid temperature")
            else:
                return("invalid temperature")
        else:
            return("enter a temperature")

    def checkP(self, location):
        if(location == "center"):
            textBox = self.pEdit_center
        elif(location == "edge"):
            textBox = self.pEdit_edge
        if(textBox.text() != ''):
            if(self.isTextNumber(textBox.text()) == True):
                return("valid P")
            else:
                return("invalid P")
        else:
            return("enter a P")

    def checkI(self, location):
        if(location == "center"):
            textBox = self.iEdit_center
        elif(location == "edge"):
            textBox = self.iEdit_edge
        if(textBox.text() != ''):
            if(self.isTextNumber(textBox.text()) == True):
                return("valid I")
            else:
                return("invalid I")
        else:
            return("enter a I")

    def checkD(self, location):
        if(location == "center"):
            textBox = self.dEdit_center
        elif(location == "edge"):
            textBox = self.dEdit_edge
        if(textBox.text() != ''):
            if(self.isTextNumber(textBox.text()) == True):
                return("valid D")
            else:
                return("invalid D")
        else:
            return("enter a D")

    def isTextNumber (self, input):
        try:
            int(input)
            return True
        except ValueError:
            return False

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

