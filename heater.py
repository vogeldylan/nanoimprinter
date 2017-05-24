'''

    ************************************************************************
    *   FILE NAME:      heater.py
    *   AUTHOR:         Dylan Vogel
    *   PURPOSE:        This file contains functions for heater control using PWM.
    *
    *
    *   EXTERNAL REFERENCES:    RPi.GPIO, thmcouple
    *
    *
    *   NOTES:           None.
    *
    *
    *   REVISION HISTORY:
    *
    *                   2017-05-22: Created file.
    *

'''


import RPi.GPIO as GPIO
import thmcouple as thm

global PWM_PIN_1, PWM_PIN_2, freq, pwm_1, pwm_2

# GPIO, not board pins on the RPi
PWM_PIN_1 = 23      # Center
PWM_PIN_2 = 24      # Edge

# PWM frequency in Hz
freq = 500

def setup():
    global pwm_1, pwm_2
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PWM_PIN_1, GPIO.OUT)
    GPIO.setup(PWM_PIN_2, GPIO.OUT)

    pwm_1 = GPIO.PWM(PWM_PIN_1, freq)
    pwm_2 = GPIO.PWM(PWM_PIN_2, freq)

    # Start both PWM channels at 0% duty cycle.
    pwm_1.start(0)
    pwm_2.start(0)

def initial_heating_time(temp1, temp2, work_temp):
    # Apply some math to figure out how long to heat for.

    temp1 = thm.read(1)
    temp2 = thm.read(2)
    avg = (temp1 + temp2) / 2.0

    heating_time = ((work_temp - avg) / 4.0) * 0.9

    return heating_time

def update_temp(temp_avg, temp):
    # Simple weighting scheme to smooth out large variations.

    new_temp = ((temp_avg * 2.0) + temp) / 3.0
    return new_temp

def change_duty(duty_1, duty_2):
    global pwm_1, pwm_2
    pwm_1.ChangeDutyCycle(duty_1)
    pwm_2.ChangeDutyCycle(duty_2)

def clamp(n, minn, maxn):
    return max(min(n, maxn), minn)

def close():
    pwm_1.stop()
    pwm_2.stop()
