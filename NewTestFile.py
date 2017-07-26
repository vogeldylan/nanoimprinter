import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QCoreApplication
import thmcouple as thm
import heater
import traceback
import time
import heatingProcess

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('heaterGUInewtest.ui', self)
        self.setUp()
        self.process = heatingProcess.heatingProcess()
        self.val = 0

    def setUp(self):
        self.outputMessage.append("Welcome")

        #Connect the buttons with their actions
        self.runButton.clicked.connect(self.handleRun)
        self.stopButton.clicked.connect(self.handleStop)

        #Disable the stop button at the start
        self.stopButton.setEnabled(False)

        #Connect combobox with its action
        self.modeSelection.currentIndexChanged.connect(self.changeIndex)

    def changeIndex(self):

        #Get the current mode selected
        self.process.mode = str(self.modeSelection.currentText())

        #If the mode selected is temperatrue mode, disable the input boxes for the PID values
        if(str(self.modeSelection.currentText()) == "Temperature mode"):
            self.changeEditStatus(False)
            self.editClear()
        else:
            self.changeEditStatus(True)

    def editClear(self):

        #Clear the input boxes for the PID values
        self.tempEdit.clear()
        self.pEdit_center.clear()
        self.iEdit_center.clear()
        self.dEdit_center.clear()
        self.pEdit_edge.clear()
        self.iEdit_edge.clear()
        self.dEdit_edge.clear()

    def changeEditStatus(self, status):

        #Enable or disable the input boxes for the PID values based on the status
        self.tempEdit.setEnabled(status)
        self.pEdit_center.setEnabled(status)
        self.iEdit_center.setEnabled(status)
        self.dEdit_center.setEnabled(status)
        self.pEdit_edge.setEnabled(status)
        self.iEdit_edge.setEnabled(status)
        self.dEdit_edge.setEnabled(status)

    def handleRun(self):

        if(self.process.mode == "Heating mode"):

            #Check the validity for the inputs for the PID values
            inputStatus = self.checkInput()

            if (inputStatus == True):
                self.outputMessage.clear()
                self.runButton.setEnabled(False)
                self.stopButton.setEnabled(True)
                self.displayMessage("Setup completed, initial heating  ... ")

                # change
                try:
                    self.process.setup()
                    # Function stored in heater.py. Algorithm based on empirical results.
                    self.process.heat_time = heater.initial_heating_time(self.process)
                    heater.change_duty(self.process)

                    #change
                    self.process.coefficients_center = self.process.pid_center.getPID()
                    self.process.coefficients_edge = self.process.pid_edge.getPID()
                    self.process.dataLog.createPlot(self)
                    self.process.dataLog.updatePlot(self)

                    # This is the initial heating.
                    while ((time.time() - self.process.start_t) < self.process.heat_time):
                        if ((time.time() - self.process.curr_t) >= self.process.data_log_freq):
                            self.process.t_center = thm.read(self.process.thm1)
                            self.process.t_edge = thm.read(self.process.thm2)

                            self.process.curr_t = time.time()
                            self.process.dataLog.write_line_to_log(self)

                    # Update PWM values to zero.
                    self.process.pwm_center = 0
                    self.process.pwm_edge = 0
                    heater.change_duty(self.process)

                    self.displayMessage('Initial heating finished...')
                    self.process.dataLog.write('LINE', round((time.time() - self.process.start_t), 2), 'Initial heating finished at: ')

                    self.process.pid_start_t = time.time()

                    #change
                    '''
                    self.process.coefficients_center = self.process.pid_center.getPID()
                    self.process.coefficients_edge = self.process.pid_edge.getPID()
                    self.process.dataLog.createPlot(self)
                    '''


                    # Wait for the temperature to settle.
                    while ((time.time() - self.process.pid_start_t) < self.process.wait_time):
                        if ((time.time() - self.process.curr_t) >= self.process.data_log_freq):
                            self.process.t_center = thm.read(self.process.thm1)
                            self.process.t_edge = thm.read(self.process.thm2)

                            self.process.curr_t = time.time()
                            self.process.dataLog.write_line_to_log(self)

                            #change
                            self.process.dataLog.updatePlot(self)
                            heater.change_duty(self.process)

                    self.displayMessage('PID controller started ...')
                    self.process.dataLog.write('LINE', round((time.time() - self.process.start_t), 2), 'PID Controller started at: ')

                    working = True
                    #limited = [[False, False], [False, False]]
                    isLimited = {'Kp_center': False, 'Kp_edge': False, 'Kd_center': False, 'Kd_edge': False, 'Ki_center': False, 'Ki_edge': False}

                    while working:
                        self.process.t_center_last = self.process.t_center
                        self.process.t_edge_last = self.process.t_edge
                        self.process.t_center = thm.read(self.process.thm1)
                        self.process.t_edge = thm.read(self.process.thm2)

                        if ((time.time() - self.process.curr_t) >= self.process.data_log_freq):
                            self.process.curr_t = time.time()
                            self.process.dataLog.write_line_to_log(self)

                            self.process.updatePlot(self)

                        self.process.t_center_avg = (self.process.t_center + self.process.t_center_last) / 2.0
                        self.process.t_edge_avg = (self.process.t_edge + self.process.t_edge_last) / 2.0

                        self.process.pid_center.update(self.process.t_center_avg)
                        self.process.pwm_center = self.process.pid_center.output
                        self.process.pwm_center = heater.clamp(self.process.pwm_center, 0, 100)

                        self.process.pid_edge.update(self.process.t_edge_avg)
                        self.process.pwm_edge = self.process.pid_edge.output
                        self.process.pwm_edge = heater.clamp(self.process.pwm_edge, 0, 100)

                        heater.change_duty(self.process)

                        # Suppress Kp once the current temp nears the working temp.
                        if ((isLimited['Kp_center'] == False) and ((self.process.temp - self.process.t_center_avg) < 15)):
                            self.displayMessage("Kp center suppressed ... ")
                            self.process.dataLog.write('LINE', 0, 'Kp center suppressed')
                            self.process.pid_center.setKp(self.process.limited_kp)
                            isLimited['Kp_center'] = True

                        if ((isLimited['Kp_edge'] == False) and ((self.process.temp - self.process.t_edge_avg) < 15)):
                            self.displayMessage("Kp edge suppressed ... ")
                            self.process.dataLog.write('LINE', 0, 'Kp edge suppressed')
                            self.process.pid_edge.setKp(self.process.limited_kp)
                            isLimited['Kp_edge'] = True

                        if ((isLimited['Kd_center'] == False) and ((self.process.temp - self.process.t_center_avg) < 1)):
                            self.displayMessage("Kd center suppressed ... ")
                            self.process.dataLog.write('LINE', 0, 'Kd center suppressed')
                            self.process.pid_center.setKd(self.process.limited_kd)
                            isLimited['Kd_center'] = True

                        if ((isLimited['Kd_edge'] == False) and ((self.process.temp - self.process.t_edge_avg) < 1)):
                            self.displayMessage(("Kd edge suppressed ... "))
                            self.process.dataLog.write('LINE', 0, 'Kd edge suppressed')
                            self.process.pid_edge.setKd(self.process.limited_kd)
                            isLimited['Kd_edge'] = True

                        if((isLimited['Ki_center'] == False) and ((self.process.temp - self.process.t_center_avg < 1))):
                            self.displayMessage(("Ki center suppressed ... "))
                            self.process.dataLog.write('LINE', 0, 'Ki center suppressed')
                            self.process.pid_center.setKi(self.process.limited_ki)
                            isLimited['Ki_center'] = True

                        if((isLimited['Ki_edge'] == False) and ((self.process.temp - self.process.t_edge_avg < 1))):
                            self.displayMessage(("Ki edge suppressed ... "))
                            self.process.dataLog.write('LINE', 0, 'Ki edge suppressed')
                            self.process.pid_edge.setKi(self.process.limited_ki)
                            isLimited['Ki_edge'] = True

                        # change
                        if (time.time() - self.process.start_t >= 1000):
                            working = False

                except KeyboardInterrupt:
                    self.process.dataLog.close()
                    thm.close(self.process.thm1)
                    thm.close(self.process.thm2)
                    heater.close(self.process.pwm_1)
                    heater.close(self.process.pwm_2)

                    self.process.coefficients_center = self.process.pid_center.getPID()
                    self.process.coefficients_edge = self.process.pid_edge.getPID()

                    self.process.dataLog.createPlot(self)
                    sys.exit()

                except:
                    traceback.print_exc()
                    self.process.dataLog.close()
                    thm.close(self.process.thm1)
                    thm.close(self.process.thm2)
                    heater.close(self.process.pwm_1)
                    heater.close(self.process.pwm_2)
                    sys.exit()

        else:
            #This is for the temperature mode
            self.outputMessage.clear()
            self.process.measuring = True
            self.runTemperatureMeasurement()

    def runTemperatureMeasurement(self):
        self.runButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.displayMessage("Temperature measurement starting...")
        self.process.setupTemp()
        #change
        if self.val == 0:
            self.process.dataLog.createPlotTemp(self)
        else:
            self.process.dataLog.updatePlotTemp(self)
        #Continuously measure and display the temperature until the stop button has been pressed
        while (self.process.measuring == True):
            self.process.t_center = thm.read(self.process.thm1)
            self.process.t_edge = thm.read(self.process.thm2)

            if ((time.time() - self.process.curr_t) >= self.process.data_log_freq):
                self.process.curr_t = time.time()
                self.process.dataLog.write_temp_to_log(self)
                #change
                self.process.dataLog.updatePlotTemp(self)

    def handleStop(self):

        #Stop the temperature measruement
        self.process.measuring = False
        self.runButton.setEnabled(True)
        self.stopButton.setEnabled(False)

        #Close the thermocouples, the heaters, and the data log
        if(self.process.mode == 'Heating mode'):
            thm.close(self.process.thm1)
            thm.close(self.process.thm2)
            heater.close(self.process.pwm_1)
            heater.close(self.process.pwm_2)

            self.process.coefficients_center = self.process.pid_center.getPID()
            self.process.coefficients_edge = self.process.pid_edge.getPID()

            '''
            self.outputMessage.append("\nThe process has finished. Please ensure everything is turned off.")
            self.outputMessage.update()
            QCoreApplication.processEvents()
            '''
            self.generateMessageBox("REMINDER", "The process has finished. Please ENSURE that EVERYTHING has been TURNED OFF.")

            self.process.dataLog.createPlot(self)

            self.process.dataLog.close()
        else:
            thm.close(self.process.thm1)
            thm.close(self.process.thm2)
            self.generateMessageBox("REMINDER", "The process has finished. Please ENSURE that EVERYTHING has been TURNED OFF.")

            self.process.dataLog.createPlotTemp(self)

            self.process.dataLog.close()

    def checkInput(self):

        #Check the validity of the temperature entered
        statusTemp = self.checkTemp()

        #Generate the matching dialog box for every scenario of the temperature input
        if (statusTemp == "enter a temperature"):
            self.generateMessageBox("Enter Temperature", "Please enter a temperature value")
        elif (statusTemp == "temperature too high"):
            self.generateMessageBox("Temperature too high", "The temperature value entered is too high. Please enter a value below 200.")
        elif (statusTemp == "invalid temperature"):
            self.generateMessageBox("Invalid temperature", "Please enter a valid temperature")
        elif (statusTemp == "valid temperature"):

            #Check the validity of the PID values entered
            statusP_center = self.checkP("center")
            statusI_center = self.checkI("center")
            statusD_center = self.checkD("center")

            statusP_edge = self.checkP("edge")
            statusI_edge = self.checkI("edge")
            statusD_edge = self.checkD("edge")

            #Generate the mataching dialog box for every scenario of the PID inputs
            if (statusP_center == "invalid P"):
                self.generateMessageBox("Invalid center P",
                                        "The center P value entered is invalid. Please enter a valid value")
            elif (statusP_center == "enter a P"):
                self.generateMessageBox("Enter center P value", "Please enter a center P value.")

            if (statusI_center == "invalid I"):
                self.generateMessageBox("Invalid center I",
                                        "The center I value entered is invalid. Please enter a valid value")
            elif (statusI_center == "enter a I"):
                self.generateMessageBox("Enter center I value", "Please enter a center I value.")

            if (statusD_center == "invalid D"):
                self.generateMessageBox("Invalid D",
                                        "The center D value entered is invalid. Please enter a valid value")
            elif (statusD_center == "enter a D"):
                self.generateMessageBox("Enter center D value", "Please enter a center D value.")

            if (statusP_edge == "invalid P"):
                self.generateMessageBox("Invalid edge P",
                                        "The edge P value entered is invalid. Please enter a valid value")
            elif (statusP_edge == "enter a P"):
                self.generateMessageBox("Enter edge P value", "Please enter an edge P value.")

            if (statusI_edge == "invalid I"):
                self.generateMessageBox("Invalid edge I",
                                        "The edge I value entered is invalid. Please enter a valid value")
            elif (statusI_edge == "enter a I"):
                self.generateMessageBox("Enter edge I value", "Please enter an edge I value.")

            if (statusD_edge == "invalid D"):
                self.generateMessageBox("Invalid D", "The edge D value entered is invalid. Please enter a valid value")
            elif (statusD_edge == "enter a D"):
                self.generateMessageBox("Enter edge D value", "Please enter an edge D value.")

            #Valid center PID inputs
            if (statusP_center == "valid P" and statusI_center == "valid I" and statusD_center == "valid D"):
                center_Valid = True
            else:
                center_Valid = False

            #Valid edge PID inputs
            if (statusP_edge == "valid P" and statusI_edge == "valid I" and statusD_edge == "valid D"):
                edge_Valid = True
            else:
                edge_Valid = False

            #If the center and edge PID values are all valid, store them in variables
            if (center_Valid == True and edge_Valid == True):
                self.process.temp = float(self.tempEdit.text())
                self.process.P_center = float(self.pEdit_center.text())
                self.process.I_center = float(self.iEdit_center.text())
                self.process.D_center = float(self.dEdit_center.text())
                self.process.P_edge = float(self.pEdit_edge.text())
                self.process.I_edge = float(self.iEdit_edge.text())
                self.process.D_edge = float(self.dEdit_edge.text())
                return True
            else:
                return False

    def generateMessageBox(self, title, msg):
        #Function thatt generates a dialog box
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setWindowTitle(title)
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msgBox.setText(msg)
        msgBox.exec_()

    def displayMessage(self, msg):
        #Function for displaying output message in the QTextEdit
        self.outputMessage.append(msg)
        self.outputMessage.update()
        QCoreApplication.processEvents()

    def checkTemp(self):
        #Check if the temperature input is too high, valid, invalid, or not yet entered
        if (self.tempEdit.text() != ''):
            if (self.isTextNumber(self.tempEdit.text()) == True):
                if (float(self.tempEdit.text()) > 200):
                    return ("temperature too high")
                else:
                    return ("valid temperature")
            else:
                return ("invalid temperature")
        else:
            return ("enter a temperature")

    def checkP(self, location):
        #Check if the P value is valid, invalid, or yet to be entered
        if (location == "center"):
            textBox = self.pEdit_center
        elif (location == "edge"):
            textBox = self.pEdit_edge
        if (textBox.text() != ''):
            if (self.isTextNumber(textBox.text()) == True):
                return ("valid P")
            else:
                return ("invalid P")
        else:
            return ("enter a P")

    def checkI(self, location):
        #Check if the I value is valid, invalid, or yet to be entered
        if (location == "center"):
            textBox = self.iEdit_center
        elif (location == "edge"):
            textBox = self.iEdit_edge
        if (textBox.text() != ''):
            if (self.isTextNumber(textBox.text()) == True):
                return ("valid I")
            else:
                return ("invalid I")
        else:
            return ("enter a I")

    def checkD(self, location):
        #Check if the D value is valid, invalid, or yet to be entered
        if (location == "center"):
            textBox = self.dEdit_center
        elif (location == "edge"):
            textBox = self.dEdit_edge
        if (textBox.text() != ''):
            if (self.isTextNumber(textBox.text()) == True):
                return ("valid D")
            else:
                return ("invalid D")
        else:
            return ("enter a D")

    def isTextNumber(self, input):
        #Check whether the input is an integer or not
        try:
            int(input)
            return True
        except ValueError:
            return False


