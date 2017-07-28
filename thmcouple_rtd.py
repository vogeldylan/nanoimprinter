'''

    ************************************************************************
    *   FILE NAME:      temp_rtd.py
    *   AUTHORS:         Dylan Vogel, Peter Feng
    *   PURPOSE:        This file contains functions related to RTD
    *                   measurement via the MAX31865.
    *
    *   EXTERNAL REFERENCES:    spidev
    *
    *
    *   NOTES:         Should write in fault detection functions.
    *                   DOESN'T HANDLE NEGATIVE VALUES YET
    *
    *   REVISION HISTORY:
    *
    *                   2017-07-26: Copied file from thmcouple.py
    *

'''
import spidev
import RPi.GPIO as GPIO
import time
import math

CONFIG_ADDR = 0x80
CONFIG = 0b10100001  # write this before reading.
RTD_MSB_ADDR  = 0x01
RTD_A = 0.0039083
RTD_B = -0.0000005775

GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.IN)

#Set up 1st thermocouple
def setup1():
    tc_1 = spidev.SpiDev()
    tc_1.mode = 0b01
    tc_1.open(0,0)
    tc_1.max_speed_hz = 5000000
    return tc_1

#Set up 2nd thermocouple
def setup2():
    tc_2 = spidev.SpiDev()
    tc_2.mode = 0b01
    tc_2.open(0,1)
    tc_2.max_speed_hz = 5000000
    return tc_2


def read(sensor):
    sensor.xfer2([CONFIG_ADDR, CONFIG])
    while not GPIO.input(25):
        time.delayMicroseconds(1)

    rec = sensor.xfer2([RTD_MSB_ADDR, 0x00, 0x00])
    data = (rec[1] << 8 | rec[2] >> 1)

    Rt = (data * 430)

    Z1 = -RTD_A
    Z2 = RTD_A * RTD_A - (4 * RTD_B)
    Z3 = (4 * RTD_B) / 100
    Z4 = 2 * RTD_B

    temp = Z2 + (Z3 * Rt)
    temp = (math.sqrt(temp) + Z1) / Z4

    if (temp >= 0):
        return temp

def close(sensor):
    sensor.close()
