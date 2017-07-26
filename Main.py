#!/usr/bin/python

'''
    ************************************************************************
    *   FILE NAME:      main.py
    *   AUTHOR:         Dylan Vogel, Peter Feng
    *   PURPOSE:        This file contains the script used to run the nanoimprinting process.
    *
    *
    *   EXTERNAL REFERENCES:    time, sys, dataLog, thmcouple, heater, PID
    *
    *
    *   NOTES:          Script can be safely closed using Ctrl-C.
    *
    *
    *   REVISION HISTORY:
    *
    *                   2017-05-22: Created file.
    *                   2017-05-23: Added PWM scriping and functions related to PID controller.
    *                   2017-05-24: Added waiting time after initial heating before PID controller
    *                               activates. Adjusted PID settings based on trials.
    *                   2017-05-25: Reorganized function structure and added comments for readability.
    *                               Moved all setup values to one section and labelled them for easy adjustment.
    *                               Added a limiting Kp value that the PID controller switches to within 15 C
    *                               of the target temp.
    *                               Moved most of the main script inside the try ... except statement for
    *                               consistent logging and proper script closure.
    *                               Added an exception handler that catches non-KeyboardInterrupt exceptions, prints
    *                               them to console, and safely exits the script.
    *                               Changed the clamping mechanism to work on the edge and center elements separately.



'''

# System functions
import time
import sys
import traceback


# User functions
import dataLog as log
import thmcouple as thm
import heater
import PID
import controller
################################################################################
''' EDIT THESE; THESE ARE THE PID COEFFICIENTS '''

'''

def pid_setup_center(work_temp, P, I, D): #change

    # Written as (Kp, Ki, Kd)
    pid_center = PID.PID(P, I, D)

    # Windup to prevent integral term from going too high/low.
    pid_center.setWindup(1)

    # Sample time, pretty self-explanatory.
    pid_center.setSampleTime(0.5)
    pid_center.SetPoint = work_temp

    return pid_center

def pid_setup_edge(work_temp, P, I, D): #change

    pid_edge = PID.PID(P, I, D)

    pid_edge.setWindup(1)
    pid_edge.setSampleTime(0.5)
    pid_edge.SetPoint = work_temp

    return pid_edge
'''

if __name__ == "__main__":

    ################################################################################
    ''' EDIT THESE SETUP VARIABLES '''

    #change
    #work_temp = input('Enter a working temperature between 0-200 C: ')

    app = controller.QtWidgets.QApplication(sys.argv)
    window = controller.MainWindow()
    window.show()
    sys.exit(app.exec_())

    work_temp = window.temp
    P_center = window.P_center
    I_center = window.I_center
    D_center = window.D_center

    P_edge = window.P_edge
    I_edge = window.I_edge
    D_edge = window.D_edge



 
