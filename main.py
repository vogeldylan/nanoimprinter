#!/usr/bin/python

'''
    ************************************************************************
    *   FILE NAME:      main.py
    *   AUTHOR:         Dylan Vogel
    *   PURPOSE:        This file contains the script used to run the nanoimprinting process.
    *
    *
    *   EXTERNAL REFERENCES:    time, sys, dataLog, thmcouple, heater PID
    *
    *
    *   NOTES:
    *
    *
    *   REVISION HISTORY:
    *
    *                   2017-05-22: Created file.
    *                   2017-05-23: Added PWM scriping and functions related to PID controller.
    *                   2017-05-24: Added waiting time after initial heating before PID controller
    *                               activates. Adjusted PID settings based on trials.



'''

# System functions
import time
import sys


# User functions
import dataLog as log
import thmcouple as thm
import heater
import PID


def pid_setup_center(work_temp):

    pid_center = PID.PID(0.08, 0, -6)

    pid_center.setWindup = 2    # Not chosen for any particular reason
    pid_center.setSampleTime = 0.1
    pid_center.SetPoint = work_temp

    return pid_center

def pid_setup_edge(work_temp):

    pid_edge = PID.PID(0.1, 0, -6)

    pid_edge.setWindup = 2      # Not chosen for any particular reason
    pid_edge.setSampleTime = 0.1
    pid_edge.SetPoint = work_temp

    return pid_edge


def write_line_to_log(t_center, t_edge, pwm_center, pwm_edge, curr_t, start_t, cent_temps, edge_temps, times):

    d_time = round((curr_t - start_t), 2)

    times.append(d_time)
    cent_temps.append(t_center)
    edge_temps.append(t_edge)

    log.write('COL', [d_time, t_center, t_edge, pwm_center, pwm_edge], ['Time: ','Temp_1: ', 'Temp_2: ', 'Duty_center: ', 'Duty_edge: '])
    print('Time: ' + str(d_time) + '\t' + 'Temp_1: ' + str(t_center) + '\t' + 'Temp_2: ' + str(t_edge) + '\t' + 'Duty_center: ' + str(pwm_center) +  '\t' + 'Duty_edge: ' + str(pwm_edge))


if __name__ == "__main__":

    work_temp = input('Enter a working temperature between 0-200 C: ')
    #heat_time = input('Enter bonding time in seconds 0-3600s: ')

    log.setup("PID_cartridge_test")
    thm.setup()
    heater.setup()
    pid_edge = pid_setup_edge(work_temp)
    pid_center = pid_setup_center(work_temp)

    data_log_freq = 1

    print ("Setup completed, initial heating  ... ")

    t_center = thm.read(1)
    t_center_avg = t_center
    t_edge = thm.read(2)
    t_edge_avg = t_edge

    heat_time = heater.initial_heating_time(t_center, t_edge, work_temp)

    start_t = time.time()
    curr_t = time.time()

    times = []
    cent_temps = []
    edge_temps = []

    pwm_center = 50    # Center
    pwm_edge = 100    # Edge

    heater.change_duty(pwm_center, pwm_edge)

    try:
        while ((time.time() - start_t) < heat_time):
            if ((time.time() - curr_t) >= data_log_freq):
                t_center = thm.read(1)
                t_edge = thm.read(2)

                curr_t = time.time()
                write_line_to_log(t_center, t_edge, pwm_center, pwm_edge, curr_t, start_t, cent_temps, edge_temps, times)

    except KeyboardInterrupt:
            log.close()
            thm.close()
            heater.close()

            sys.exit()

    # Initial heating done, time for some PID controller.
    pwm_center = 0
    pwm_edge = 0
    heater.change_duty(pwm_center, pwm_edge)

    print('Initial heating finished...')
    log.write('LINE', curr_t, 'Initial heating finished at: ')

    working = True
    pid_start_t = time.time()

    # This while loop just chills on the PID controller for 15s while the temperature settles.
    while ((time.time() - pid_start_t) < 15):
        try:
            if ((time.time() - curr_t) >= data_log_freq):
                t_center = thm.read(1)
                t_edge = thm.read(2)

                curr_t = time.time()
                write_line_to_log(t_center, t_edge, pwm_center, pwm_edge, curr_t, start_t, cent_temps, edge_temps, times)

        except KeyboardInterrupt:
            log.close()
            thm.close()
            heater.close()

            log.createPlot(times, cent_temps, edge_temps, heat_time)

            sys.exit()

    print('PID controller started ...')
    log.write('LINE', curr_t, 'PID Controller started at: ')

    while working:
        try:
            t_center = thm.read(1)
            t_edge = thm.read(2)

            if ((time.time() - curr_t) >= data_log_freq):

                curr_t = time.time()
                write_line_to_log(t_center, t_edge, pwm_center, pwm_edge, curr_t, start_t, cent_temps, edge_temps, times)

            if ((time.time() - pid_start_t) > 15):
                t_center_avg = heater.update_temp(t_center_avg, t_center)
                t_edge_avg = heater.update_temp(t_edge_avg, t_edge)

                pid_center.update(t_center_avg)
                pwm_center = pid_center.output
                pwm_center = heater.clamp(pwm_center, 0, 100)

                pid_edge.update(t_edge_avg)
                pwm_edge = pid_edge.output
                pwm_edge = heater.clamp(pwm_edge, 0, 100)

                heater.change_duty(pwm_center, pwm_edge)

        except KeyboardInterrupt:
            log.close()
            thm.close()
            heater.close()

            
            log.createPlot(times, cent_temps, edge_temps, heat_time)

            sys.exit()
