'''
    *******************************************************************************************************************
    *   FILE NAME:      heatingProcess.py
    *   AUTHOR:         Yu Dong (Peter) Feng, Dylan Vogel
    *   PURPOSE:        This file contains the heatingProcess class, which is used for heating and temperature tests.
    *******************************************************************************************************************
'''

import pid_setup
import dataLogClass as log
import thmcouple as thm
import heater
import time

class heatingProcess:
    def __init__(self):

        #The frequency of temperature recording
        self.data_log_freq = 1

        # The PWM duty used for the initial heating. Generally around 50% for the
        # center and 100% for the edge seems to work. Should be adjusted based on
        # changes to the thermal volume based on empirical results.
        self.pwm_center = 20
        self.pwm_edge = 100

        # Used to suppress Kp as it approaches the setpoint.
        self.limited_kp = 1  # heater.calc_kp(work_temp)

        self.limited_ki = 0.5

        self.limited_kd = 0.5

        # Time to wait after initial heating for temp to settle
        self.wait_time = 30

        self.temp = 0
        self.P_center = 0
        self.I_center = 0
        self.D_center = 0
        self.P_edge = 0
        self.I_edge = 0
        self.D_edge = 0
        self.mode = "Heating mode"
        self.measuring = False

        #Setting up the initial parameters for determining the initial heat time
        self.mass = 30
        self.heat_capacity = 50
        self.watt = 1700

    def setup(self):
        #Setup for heating mode

        #Setup datalog
        self.dataLog = log.dataLog("PID_cartridge_test")

        #Setup thermocouple
        self.thm1 = thm.setup1()
        self.thm2 = thm.setup2()

        #Setup heater
        self.pwm_1 = heater.setup1()
        self.pwm_2 = heater.setup2()

        #Setup PID
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

        #Lists used for graph plotting
        self.times = []
        self.cent_temps = []
        self.edge_temps = []

    def setupTemp(self):
        #Setup for temperature mode. Very similar to the setup for the heater mode except that PID is not used.
        self.dataLog = log.dataLog("Temperature_Measurement_Test")

        self.thm1 = thm.setup1()
        self.thm2 = thm.setup2()

        self.t_center = thm.read(self.thm1)
        self.t_edge = thm.read(self.thm2)

        # These variables store the temperature averaged over the last two values.
        self.t_center_avg = self.t_center
        self.t_edge_avg = self.t_edge

        self.start_t = time.time()
        self.curr_t = time.time()

        self.times = []
        self.cent_temps = []
        self.edge_temps = []