#!/usr/bin/python

'''
Some scratch code written to compliment run_heating_plate_ver2.py


'''

# System functions
import time
import sys
import matplotlib.pyplot as plt

# User functions
import dataLog as log
import thmcouple as thm
import heater

def pid_setup():
    # Right now these are just taken directly from the existing code.
    # This section is the one that should be tuned to adjust heating.

    pid1 = PID.PID()
    pid2 = PID.PID()

    pid1.Kp = 1.0
    pid1.Ki = 0.75
    pid1.Kd = 0.25

    pid2.Kp = 1.0
    pid2.Ki = 0.75
    pid2.Kd = 0.25

    pid1.Integrator_max = 30
    pid1.Integrator_min = -40
    pid2.Integrator_max = 30
    pid2.Integrator_min = -40


if __name__ == "__main__":

    log.setup("temperature_log")
    thm.setup()
    heater.setup()

    data_log_freq = 1

    print "Reading Temperature  ... "

    temp1 = thm.read(1)
    temp2 = thm.read(2)

    heat_time = 25 #heater.initial_heating_time(temp1, temp2, work_temp)

    start_t = time.time()
    curr_t = time.time()

    times = []
    temps_1 = []
    temps_2 = []

    duty_1 = 50    # Center
    duty_2 = 100    # Edge

    #heater.change_duty(duty_1, duty_2)

    '''while ((time.time() - start_t) < heat_time):
        if ((time.time() - curr_t) >= data_log_freq):

            curr_t = time.time()
            d_time = round((curr_t - start_t), 2)

            temp1 = thm.read(1)
            temp2 = thm.read(2)

            times.append(d_time)
            temps_1.append(temp1)
            temps_2.append(temp2)

            log.write('COL', [d_time, temp1, temp2, duty_1, duty_2], ['Time: ', 'Temp_1: ', 'Temp_2: ', 'Duty_1: ', 'Duty_2: '])
            print('Time: ' + str(d_time) + '\t' + 'Temp_1: ' + str(temp1) + '\t' + 'Temp_2: ' + str(temp2))

    heater.change_duty(0, 0)'''

    working = True
    #print('Cooling ... ')

    while working:
        try:
            curr_t = time.time()
            d_time = round((curr_t - start_t), 2)

            temp1 = thm.read(1)
            temp2 = thm.read(2)

            times.append(d_time)
            temps_1.append(temp1)
            temps_2.append(temp2)
            
            log.write('COL', [d_time, temp1, temp2], ['Time: ','Temp_1 (ºC): ', 'Temp_2 (ºC): '])
            print('Time: ' + str(d_time) + '\t' + 'Temp_1: ' + str(temp1) + '\t' + 'Temp_2: ' + str(temp2))
            time.sleep(1)
            '''
            log.write('LINE', thm.read(1), 'Temp_1 (C): ')
            time.sleep(1)'''
        except KeyboardInterrupt:
            log.close()
            thm.close()
            heater.close()

            plt.plot(times, temps_1, 'r', times, temps_2, 'g')
            plt.ylabel('Temperature (C)')
            plt.xlabel('Time From Start (s)')
            plt.title('Heating Characteristics for Circular Heater')
            plt.savefig('figure.pdf')
            
            sys.exit()
