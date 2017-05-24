'''

    ************************************************************************
    *   FILE NAME:      dataLog.py
    *   AUTHOR:         Dylan Vogel
    *   PURPOSE:        This file contains functions used for logging the results
    *                   of heater tests
    *
    *   EXTERNAL REFERENCES:    os, time
    *
    *
    *   NOTES:          None.
    *
    *
    *   REVISION HISTORY:
    *
    *                   2017-05-22: Created file.
    *                   2017-05-23: Wrote a function for creating plots.

'''

import os
import time
import matplotlib.pyplot as plt

global datafile


def setup(label):
    global datafile

    t = time.localtime()
    dir_name = str(t.tm_year) + '-' + str(t.tm_mon) + '-' + str(t.tm_mday)

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        os.chmod(dir_name, 0777)

    file_name = label + '-' + str(t.tm_hour) + '-' + str(t.tm_min) + '-' + str(t.tm_sec)
    datafile = open(dir_name + '/' + file_name, 'a')
    '''
    datafile.write('Working temperature:' + str(work_temp)+ '\n' )
    datafile.write('Safe temperature:' + str(safe_temp)+ '\n' )
    datafile.write('Bonding time:' + str(heat_time) + '\n')
    datafile.write('PWM frequency:' + str(pwm_freq) + '\n')
    datafile.write('PID parameter SSR1: Kp/Ki/Kd:' + str(pid1.Kp) + '\t\t' + str(pid1.Ki) +'\t\t'+ str(pid1.Kd) +'\n')
    datafile.write('PID parameter SSR2: Kp/Ki/Kd:' + str(pid2.Kp) + '\t\t' + str(pid2.Ki) +'\t\t'+ str(pid2.Kd)+'\n')
    datafile.write('Time (s) \tTemp1 (C) \tTemp2 (C) \tDutyCycle1 \tDutyCycle2 \n')   # Column header
    '''
def write(type, data, message):
    ''' Valid types (thus far):
        COL
        LINE
    '''
    if (type == 'COL'):
        for i in range(0,len(data)):
            datafile.write(message[i] + str(data[i]) + '\t')
        datafile.write('\n')
    elif (type == 'LINE'):
        datafile.write(message + str(data) + '\n')

def createPlot(x, y1, y2, heat_time):
    plt.plot(x, y1, 'r', x, y2, 'b')
    plt.ylabel('Temperature (C)')
    plt.xlabel('Time From Start (s)')
    plt.title('Heating Characteristics for ' + str(heat_time) + 's Pulse and PID')
    plt.savefig('figure.pdf')

def close():
    datafile.close()
